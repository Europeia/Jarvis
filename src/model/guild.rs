use crate::db::mysql::SQL_INSTANCE;
use serenity::model::id::*;
use sqlx::{Executor, MySql};
use std::{error::Error, os::unix::prelude::CommandExt};

pub struct Guild {
    pub id: GuildId,
    pub welcome_message: String,
    pub gate_data: GateData,
    pub role_data: Vec<RoleData>,
}

pub struct GateData {
    pub allow_rejoin: bool,
    pub gate_enabled: bool,
    pub key_role_id: u64,
    pub keyed_users: Vec<KeyedUser>,
}

pub struct ForeignIdType {
    pub id: i32,
    pub type_name: String,
}

pub struct KeyedUser {
    pub user_id: u64,
    pub foreign_id: String,
    pub foreign_id_type: i32,
}

pub struct RoleData {
    pub id: RoleId,
    pub can_join: bool,
    pub name: String,
    pub commanders: Vec<UserId>,
}

impl Guild {
    pub async fn save(&self) -> Result<(), Box<dyn Error>> {
        let id = self.id.as_u64();
        let welcome_message = self.welcome_message.clone();
        let query_str =
            "INSERT guild(id, welcome_message) values(?, ?) ON DUPLICATE KEY UPDATE id=values(id),welcome_message=values(welcome_message);";
        let query = sqlx::query::<MySql>(query_str).bind(id).bind(welcome_message);

        let pool = SQL_INSTANCE.lock().unwrap().pool.clone().unwrap();

        query.execute(&pool).await?;

        self.gate_data.save(self.id).await?;

        for role in &self.role_data {
            role.save(self.id).await?;
        }

        return Ok(());
    }
}

impl GateData {
    pub async fn save(&self, guild_id: GuildId) -> Result<(), Box<dyn Error>> {
        let mut query_str = String::from("INSERT guild(id, allow_rejoin, gate_enabled, key_role_id) values(?, ?, ?, ?) ");
        query_str.push_str(
            "ON DUPLICATE KEY UPDATE allow_rejoin=values(allow_rejoin),gate_enabled=values(gate_enabled),key_role_id=values(key_role_id)",
        );

        let query = sqlx::query::<MySql>(&query_str)
            .bind(guild_id.as_u64())
            .bind(if self.allow_rejoin { 1 } else { 0 })
            .bind(if self.gate_enabled { 1 } else { 0 })
            .bind(self.key_role_id);

        let pool = SQL_INSTANCE.lock().unwrap().pool.clone().unwrap();

        query.execute(&pool).await?;

        let delete_keyed_users_str: String = String::from("DELETE FROM keyed_users WHERE guild_id=?");
        let delete_query = sqlx::query::<MySql>(&delete_keyed_users_str).bind(guild_id.as_u64());
        delete_query.execute(&pool).await?;

        for ku in &self.keyed_users {
            ku.save(guild_id).await?;
        }

        return Ok(());
    }
}

impl RoleData {
    pub async fn save(&self, guild_id: GuildId) -> Result<(), Box<dyn Error>> {
        let mut query_str = String::from("INSERT role(role_id, guild_id, can_join, name) values(?, ?, ?, ?)");
        query_str.push_str("ON DUPLICATE KEY UPDATE guild_id=values(guild_id),can_join=values(can_join),name=values(name);");

        let query = sqlx::query::<MySql>(&query_str)
            .bind(self.id.as_u64())
            .bind(guild_id.as_u64())
            .bind(if self.can_join { 1 } else { 0 })
            .bind(self.name.clone());

        let pool = SQL_INSTANCE.lock().unwrap().pool.clone().unwrap();

        query.execute(&pool).await?;

        let delete_comm_str: String = String::from("DELETE FROM role_commanders WHERE role_id=?");
        let delete_query = sqlx::query::<MySql>(&delete_comm_str).bind(self.id.as_u64());
        delete_query.execute(&pool).await?;

        if self.commanders.len() > 0 {
            let mut comm_query_str = String::from("INSERT role_commanders(role_id, user_id) VALUES");
            let mut values: Vec<String> = Vec::<String>::new();
            for uid in self.commanders.iter() {
                values.push(format!("({}, {})", self.id.as_u64(), uid.as_u64()));
            }
            comm_query_str.push_str(&values.join(", ").to_string());

            let comm_query = sqlx::query::<MySql>(&comm_query_str);
            comm_query.execute(&pool).await?;
        }
        return Ok(());
    }
}

impl KeyedUser {
    pub async fn save(&self, guild_id: GuildId) -> Result<(), Box<dyn Error>> {
        let mut query_str = String::from("INSERT keyed_users(guild_id, user_id, foreign_id, foreign_id_type) values(?, ?, ?, ?) ");
        query_str.push_str("ON DUPLICATE KEY UPDATE foreign_id=values(foreign_id),foreign_id_type=values(foreign_id_type);");

        let query = sqlx::query::<MySql>(&query_str)
            .bind(guild_id.as_u64())
            .bind(self.user_id)
            .bind(self.foreign_id.clone())
            .bind(self.foreign_id_type.clone());

        let pool = SQL_INSTANCE.lock().unwrap().pool.clone().unwrap();

        query.execute(&pool).await?;

        return Ok(());
    }
}

pub async fn save_guilds(buffer: &String) -> Result<(), Box<dyn std::error::Error>> {
    let mut json: serde_json::Value = serde_json::from_str(&buffer).expect("JSON was not well-formatted");
    if !json.is_object() {
        println!("{}", &buffer);
        bail!("Json object not found!")
    }

    for (k, v) in &mut json.as_object_mut().unwrap().iter_mut() {
        let id: u64 = k.as_str().parse().unwrap();
        let guild_id: GuildId = GuildId(id);
        let guild_json = &mut v.as_object_mut().unwrap();

        let gate_json = guild_json.get_mut("gate_data").unwrap();
        let mut keyed_users = Vec::<KeyedUser>::new();
        for (uid, fuid) in &mut gate_json.get_mut("keyed_users").unwrap().as_object_mut().unwrap().iter_mut() {
            let user_id: u64 = uid.as_str().parse().unwrap();
            let mut foreign_id: String = String::from("");
            if fuid.is_string() {
                foreign_id = fuid.as_str().unwrap().to_string().clone();
            } else if fuid.is_number() {
                foreign_id = fuid.as_i64().unwrap().to_string().clone();
            }

            let keyed_user: KeyedUser = KeyedUser {
                user_id,
                foreign_id,
                foreign_id_type: 1,
            };

            keyed_users.push(keyed_user);
        }

        let gate_data: GateData = GateData {
            allow_rejoin: gate_json.get("allow_rejoin").unwrap().as_bool().unwrap(),
            gate_enabled: gate_json.get("gate_enabled").unwrap().as_bool().unwrap(),
            key_role_id: gate_json.get("key_role_id").unwrap().as_u64().unwrap(),
            keyed_users,
        };

        let role_json = guild_json.get_mut("role_data").unwrap();
        let mut role_data: Vec<RoleData> = Vec::<RoleData>::new();
        for (rid, rdat) in &mut role_json.as_object_mut().unwrap().iter() {
            let mut commanders = Vec::<UserId>::new();
            let commanders_json = rdat.get("commanders").unwrap().as_array().unwrap();
            for c in commanders_json.iter() {
                commanders.push(UserId(c.as_u64().unwrap()));
            }

            let role: RoleData = RoleData {
                id: RoleId(rid.parse().unwrap()),
                can_join: rdat.get("can_join").unwrap().as_bool().unwrap(),
                name: rdat.get("name").unwrap().as_str().unwrap().to_string(),
                commanders,
            };

            role_data.push(role);
        }

        let guild: Guild = Guild {
            id: guild_id,
            welcome_message: guild_json.get("greeting_message").unwrap().as_str().unwrap().to_string(),
            gate_data,
            role_data,
        };

        let result = guild.save().await;
        if result.is_err() {
            println!("Error Saving Guild! {:?}", &result);
        } else {
            println!("Saved Guild: {}", id);
        }
    }

    return Ok(());
}
