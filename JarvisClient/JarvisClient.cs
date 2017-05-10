using Discord.Commands;
using Discord.WebSocket;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.IO;
using System.Threading.Tasks;

namespace JarvisClient
{
    public class JarvisClient
    {
        public static void Main(string[] args) => new JarvisClient().MainAsync().GetAwaiter().GetResult();

        private DiscordSocketClient _client;

        public async Task MainAsync()
        {
            _client = new DiscordSocketClient();
            string token = "";

            using (StreamReader reader = new StreamReader("jarvisconfig.json"))
            {
                token = reader.ReadToEnd();
            }

            if(string.IsNullOrWhiteSpace(token))
            {
                Console.WriteLine("Unable to find token!  Fill in file jarvisconfig.json!");
                return;
            }

            await _client.LoginAsync(Discord.TokenType.Bot, token);
            await _client.StartAsync();


            CommandHandler handler = new CommandHandler(ConfigureServices());
            await handler.ConfigureAsync();

            await Task.Delay(-1);
        }

        private IServiceProvider ConfigureServices()
        {
            IServiceCollection services = new ServiceCollection()
                .AddSingleton(_client)
                .AddSingleton(new CommandService(new CommandServiceConfig { CaseSensitiveCommands = false, ThrowOnError = false }));

            IServiceProvider provider = new DefaultServiceProviderFactory().CreateServiceProvider(services);

            return provider;
        }
    }
}
