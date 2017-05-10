using Discord.Commands;
using Discord.WebSocket;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Reflection;
using System.Threading.Tasks;

namespace JarvisClient
{
    public class CommandHandler
    {
        private CommandService _commands;
        private DiscordSocketClient _client;
        private IServiceProvider _provider;

        public CommandHandler(IServiceProvider provider)
        {
            _provider = provider;
            _client = _provider.GetService<DiscordSocketClient>();
            _commands = _provider.GetService<CommandService>();
            _client.MessageReceived += HandleCommand;
        }

        public async Task ConfigureAsync()
        {
            await _commands.AddModulesAsync(Assembly.GetEntryAssembly());
        }

        public async Task HandleCommand(SocketMessage parameterMessage)
        {
            SocketUserMessage message = parameterMessage as SocketUserMessage;
            if (message == null)
            {
                return;
            }

            int argPos = 0;
            if (!(message.HasMentionPrefix(_client.CurrentUser, ref argPos) || message.HasCharPrefix('!', ref argPos)))
            {
                return;
            }

            SocketCommandContext context = new SocketCommandContext(_client, message);

            Console.WriteLine($"Message: {message}");

            var result = await _commands.ExecuteAsync(context, argPos);

            if (!result.IsSuccess)
            {
                await message.Channel.SendMessageAsync($"**Error:** {result.ErrorReason}");
            }
        }
    }
}
