use crate::config;
use mysql::*;
use std::error::Error;
use std::result::Result;

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
