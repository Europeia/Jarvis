use serde::{Deserialize, Serialize};
use std::fs::File;

#[derive(Serialize, Deserialize, Clone)]
pub struct SQLConfig {
    pub host: String,
    pub user: String,
    pub pw: String,
    pub db: String,
}

#[derive(Serialize, Deserialize)]
pub struct Config {
    pub token: String,
    pub application_id: u64,
    pub mysql: SQLConfig,
}

pub fn get_config() -> Result<Config, Box<dyn std::error::Error>> {
    let f = File::open("config.yaml")?;
    let config: Config = serde_yaml::from_reader(f)?;
    return Ok(config);
}
