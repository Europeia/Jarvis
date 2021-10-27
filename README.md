# Jarvis

J.A.R.V.I.S. is an Administrative helper Discord bot written in Rust against the serenity library.

## GETTING STARTED

### System requirements

rustup
MySQL 8.0+

### Installation

1. Set up your configuraiton.  config.yaml.example is an example yaml file for configuration.  Fill in the fields with information for your environment.
2. Built it
        
        cargo build --release

3. That's it!

### Usage

    jarvis [-i <filename>]
      Without any arguments, will start the bot and listen based on configuration information in config.yaml.

      Flags:
      -i -- Import a json data file and exit
