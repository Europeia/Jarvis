use crate::db::mysql::SQL_INSTANCE;
use serenity::model::id::*;
use sqlx::{Executor, MySql};
use std::error::Error;

pub struct Guild {
    id: GuildId,
    welcome_message: String,
    gate_data: GateData,
    role_data: RoleDataCollection,
}

pub struct GateData {
    allow_rejoin: bool,
    gate_enabled: bool,
    key_role_id: u64,
    keyed_users: Vec<KeyedUser>,
}

pub struct ForeignIdType {
    id: i32,
    type_name: String,
}

pub struct KeyedUser {
    user_id: u64,
    foreign_id: String,
    foreign_id_type: i32,
}

pub type RoleDataCollection = Vec<RoleData>;

pub struct RoleData {
    id: u64,
    can_join: bool,
    name: String,
    commanders: Vec<UserId>,
}

impl Guild {
    async fn save(&self) -> Result<(), Box<dyn Error>> {
        let pool = SQL_INSTANCE.lock().unwrap().pool.clone().unwrap();
        let id = self.id.as_u64();
        let query = sqlx::query::<MySql>("INSERT guild(id, welcome_message) values(?, ?)")
            .bind(id)
            .bind(self.welcome_message.clone());

        query.execute(&pool).await?;

        self.gate_data.save()?;
        self.role_data.save()?;

        return Ok(());
    }
}

impl GateData {
    fn save(&self) -> Result<(), Box<dyn Error>> {
        for ku in &self.keyed_users {
            ku.save().unwrap();
        }

        return Ok(());
    }
}

impl ForeignIdType {
    fn save(&self) -> Result<(), Box<dyn Error>> {
        return Ok(());
    }
}

impl KeyedUser {
    fn save(&self) -> Result<(), Box<dyn Error>> {
        return Ok(());
    }
}

trait ManagedRoleDataCollectionExt {
    fn save(&self) -> Result<(), Box<dyn Error>>;
}

impl ManagedRoleDataCollectionExt for RoleDataCollection {
    fn save(&self) -> Result<(), Box<dyn Error>> {
        return Ok(());
    }
}

impl RoleData {
    fn save(&self) -> Result<(), Box<dyn Error>> {
        return Ok(());
    }
}
