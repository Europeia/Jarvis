using Discord;
using Discord.Commands;
using Discord.WebSocket;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;


namespace JarvisClient.Modules
{
    [Name("RoleManager")]
    [RequireContext(ContextType.Guild)]
    public class RoleManager : ModuleBase<SocketCommandContext>
    {
        [Command("addrole", RunMode = RunMode.Async)]
        [Priority(1000)]
        public async Task AddRoleToUser(string role, string user)
        {
            IGuildUser author = (IGuildUser)Context.Message.Author;
            string okUser = "";
            if (author.Username != okUser && !author.GuildPermissions.ManageRoles)
            {
                await Context.Channel.SendMessageAsync("**Permission Denied**");
                return;
            }

            if (!Context.Guild.Roles.Any(r => r.Name == role))
            {
                await ReplyAsync($"**Invalid Role:** {role}");
                return;
            }

            SocketGuildUser targetUser = Context.Guild.Users.Where(u => $"{u.Username}#{u.Discriminator}" == user).DefaultIfEmpty(null).FirstOrDefault();

            if (targetUser == null)
            {
                await ReplyAsync($"**Invalid User:** {user}");
                return;
            }

            string displayName = string.IsNullOrWhiteSpace(targetUser.Nickname) ? targetUser.Username : targetUser.Nickname;

            SocketRole targetRole = Context.Guild.Roles.Where(r => r.Name == role).DefaultIfEmpty(null).FirstOrDefault();

            if (targetUser.Roles.Any(r => r.Id == targetRole.Id))
            {
                await ReplyAsync($"**{displayName} already has role {targetRole.Name}**");
                return;
            }

            List<SocketRole> roles = new List<SocketRole>();
            var roleIds = author.RoleIds;
            foreach(ulong roleId in roleIds)
            {
                roles.Add(Context.Guild.GetRole(roleId));
            }
            int topLevel = roles.OrderBy(r => r.Position).Last().Position;

            if(targetRole.Position >= topLevel)
            {
                await ReplyAsync($"**You cannot grant role {targetRole.Name}**");
                return;
            }

            await targetUser.AddRoleAsync(targetRole);
            await ReplyAsync($"**{displayName} granted {targetRole.Name} role.**");
        }

        [Command("remrole", RunMode = RunMode.Async)]
        [Priority(1000)]
        public async Task RemoveRoleFromUser(string role, string user)
        {
            IGuildUser author = (IGuildUser)Context.Message.Author;
            string okUser = "";
            if (author.Username != okUser && !author.GuildPermissions.ManageRoles)
            {
                await Context.Channel.SendMessageAsync("**Permission Denied**");
                return;
            }

            if (!Context.Guild.Roles.Any(r => r.Name == role))
            {
                await ReplyAsync($"**Invalid Role:** {role}");
                return;
            }

            SocketGuildUser targetUser = Context.Guild.Users.Where(u => $"{u.Username}#{u.Discriminator}" == user).DefaultIfEmpty(null).FirstOrDefault();

            if (targetUser == null)
            {
                await ReplyAsync($"**Invalid User:** {user}");
                return;
            }

            string displayName = string.IsNullOrWhiteSpace(targetUser.Nickname) ? targetUser.Username : targetUser.Nickname;

            SocketRole targetRole = Context.Guild.Roles.Where(r => r.Name == role).DefaultIfEmpty(null).FirstOrDefault();

            if (!targetUser.Roles.Any(r => r.Id == targetRole.Id))
            {
                await ReplyAsync($"**{displayName} does not have role {targetRole.Name}**");
                return;
            }

            List<SocketRole> roles = new List<SocketRole>();
            var roleIds = author.RoleIds;
            foreach (ulong roleId in roleIds)
            {
                roles.Add(Context.Guild.GetRole(roleId));
            }
            int topLevel = roles.OrderBy(r => r.Position).Last().Position;

            if (targetRole.Position >= topLevel)
            {
                await ReplyAsync($"**You cannot revoke role {targetRole.Name}**");
                return;
            }

            await targetUser.RemoveRoleAsync(targetRole);
            await ReplyAsync($"**{displayName} removed from {targetRole.Name} role.**");
        }
    }
}
