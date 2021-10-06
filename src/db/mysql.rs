use crate::config;
use lazy_static::lazy_static;
use sqlx::mysql::*;
use sqlx::pool::PoolConnection;
use std::error::Error;
use std::result::Result;
use std::sync::Mutex;

lazy_static! {
    pub static ref SQL_INSTANCE: Mutex<MySqlManager> = Mutex::new(MySqlManager::new());
}

pub struct MySqlManager {
    pub initialized: bool,
    pub config: Option<MySqlConnectOptions>,
    pub pool: Option<MySqlPool>,
}

impl MySqlManager {
    pub const fn new() -> Self {
        Self {
            initialized: false,
            config: None,
            pool: None,
        }
    }

    pub fn init(&mut self, config: config::SQLConfig) -> Result<(), Box<dyn Error>> {
        if self.initialized {
            bail!("Already Initialized!")
        }

        self.config = Some(
            MySqlConnectOptions::new()
                .username(&config.user)
                .password(&config.pw)
                .host(&config.host)
                .database(&config.db),
        );

        self.pool = Some(MySqlPool::connect_lazy_with(self.config.clone().unwrap()));
        self.initialized = true;

        return Ok(());
    }

    pub fn get_connection(&self) -> Result<PoolConnection<MySql>, Box<dyn Error>> {
        if !self.initialized {
            bail!("Not yet Initialized!");
        }

        let conn = futures::executor::block_on(self.pool.clone().unwrap().acquire());

        return Ok(conn.unwrap());
    }
}
