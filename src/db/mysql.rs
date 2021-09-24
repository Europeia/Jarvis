use crate::config;
use lazy_static::lazy_static;
use mysql::*;
use std::error::Error;
use std::result::Result;
use std::sync::Mutex;

lazy_static! {
    pub static ref SQL_INSTANCE: Mutex<MySqlManager> = Mutex::new(MySqlManager::new());
}

pub struct MySqlManager {
    initialized: bool,
    config: Option<config::SQLConfig>,
    pool: Option<Pool>,
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

        let new_config = config.clone();

        self.config = Some(config);

        let opts = OptsBuilder::new()
            .user(Some(new_config.user))
            .db_name(Some(new_config.db))
            .ip_or_hostname(Some(new_config.host))
            .pass(Some(new_config.pw));
        let pool = Pool::new(opts);
        self.pool = Some(pool.expect("Unable to connect to database!"));
        self.initialized = true;

        return Ok(());
    }

    pub fn get_connection(&self) -> Result<PooledConn, Box<dyn Error>> {
        if !self.initialized {
            bail!("Not yet Initialized!");
        }

        let pool = self.pool.clone().expect("Pool not yet initialized");

        return Ok(pool.get_conn().expect("Unable to get connection!"));
    }
}
