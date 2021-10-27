#[macro_use]
extern crate simple_error;

use std::env;
use std::fs::*;
use std::io::Read;

use model::guild::*;

use serenity::{
    async_trait,
    client::*,
    model::{
        gateway::Ready,
        id::GuildId,
        interactions::{
            application_command::{ApplicationCommand, ApplicationCommandInteractionDataOptionValue, ApplicationCommandOptionType},
            Interaction, InteractionResponseType,
        },
    },
};

mod config;
mod db;
mod model;

use db::mysql::SQL_INSTANCE;

struct Handler;

#[async_trait]
impl EventHandler for Handler {
    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::ApplicationCommand(command) = interaction {
            let content = match command.data.name.as_str() {
                "ping" => "Hey, I'm alive!".to_string(),
                "id" => {
                    let options = command
                        .data
                        .options
                        .get(0)
                        .expect("Expected user option")
                        .resolved
                        .as_ref()
                        .expect("Expected user object");

                    if let ApplicationCommandInteractionDataOptionValue::User(user, _member) = options {
                        format!("{}'s id is {}", user.tag(), user.id)
                    } else {
                        "Please provide a valid user".to_string()
                    }
                }
                _ => "not implemented :(".to_string(),
            };

            if let Err(why) = command
                .create_interaction_response(&ctx.http, |response| {
                    response
                        .kind(InteractionResponseType::ChannelMessageWithSource)
                        .interaction_response_data(|message| message.content(content))
                })
                .await
            {
                println!("Cannot respond to slash command: {}", why);
            }
        }
    }

    async fn ready(&self, ctx: Context, ready: Ready) {
        println!("{} is connected!", ready.user.name);

        let commands = ApplicationCommand::set_global_application_commands(&ctx.http, |commands| {
            commands
                .create_application_command(|command| command.name("ping").description("A ping command"))
                .create_application_command(|command| {
                    command.name("id").description("Get a user id").create_option(|option| {
                        option
                            .name("id")
                            .description("The user to lookup")
                            .kind(ApplicationCommandOptionType::User)
                            .required(true)
                    })
                })
                .create_application_command(|command| {
                    command
                        .name("welcome")
                        .description("Welcome a user")
                        .create_option(|option| {
                            option
                                .name("user")
                                .description("The user to welcome")
                                .kind(ApplicationCommandOptionType::User)
                                .required(true)
                        })
                        .create_option(|option| {
                            option
                                .name("message")
                                .description("The message to send")
                                .kind(ApplicationCommandOptionType::String)
                                .required(true)
                                .add_string_choice("Welcome to our cool server! Ask me if you need help", "pizza")
                                .add_string_choice("Hey, do you want a coffee?", "coffee")
                                .add_string_choice("Welcome to the club, you're now a good person. Well, I hope.", "club")
                                .add_string_choice("I hope that you brought a controller to play together!", "game")
                        })
                })
        })
        .await;

        println!("I now have the following global slash commands: {:#?}", commands);

        for guild_id in ctx.cache.guilds().await.iter() {
            println!("Fetching data for {}", guild_id.as_u64());
            let guild = ctx.cache.guild(guild_id).await.unwrap();
            let new_guild = Guild::new(Some(&guild), Some(true)).await;
            println!("Found data for {}:", guild_id.as_u64().clone());
            println!("{:?}", new_guild);
        }

        let guild_command = GuildId(129372441083379712)
            .create_application_command(&ctx.http, |command| {
                command.name("wonderful_command").description("An amazing command")
            })
            .await;

        println!("I created the following guild command: {:#?}", guild_command);
    }
}

#[tokio::main]
#[allow(const_item_mutation)]
async fn main() {
    let args: Vec<String> = env::args().collect();

    println!("Checking Database Connectivity...");
    let config_result = config::get_config();
    if config_result.is_err() {
        println!("Unable to get config file");
        return;
    }

    let config = config_result.unwrap();

    if SQL_INSTANCE.lock().unwrap().init(config.mysql).is_err() {
        println!("Cannot initialize connection to database");
        return;
    }

    if SQL_INSTANCE.lock().unwrap().get_connection().is_err() {
        println!("Unable to get connection to database");
        return;
    }

    let import_position = args.iter().position(|a| a == "-i");
    if !import_position.is_none() {
        let file_position = import_position.unwrap() + 1;
        let file_name_opt = args.get(file_position);
        if file_name_opt.is_none() {
            println!("Missing file name!  Usage: jarvis -i <filename>");
            return;
        }

        let file_name = file_name_opt.unwrap();

        let mut buffer = String::new();
        let f = File::open(file_name);
        if f.is_err() {
            println!("Invalid File: {}", file_name);
            return;
        }

        if f.unwrap().read_to_string(&mut buffer).is_err() {
            println!("Unable to read file - {}", file_name);
            return;
        }

        let _ = import_guilds_from_file(&buffer).await;
        // We don't want to connect. Import and finish.
        return;
    }

    let client = Client::builder(&config.token)
        .event_handler(Handler)
        .application_id(config.application_id)
        .await;
    if client.is_err() {
        println!("Error creating client - {:?}", client.err().unwrap());
        return;
    }

    if let Err(why) = client.unwrap().start().await {
        print!("Client error: {:?}", why);
    }
}
