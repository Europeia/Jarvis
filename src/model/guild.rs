use crate::db::mysql::SQL_INSTANCE;
use serenity::model::id::*;
use serenity::model::*;
use sqlx::{mysql::MySqlRow, MySql, Result as SqlxResult, Row};
use std::error::Error;

#[derive(Debug)]
pub struct Guild {
    pub id: GuildId,
    pub welcome_message: String,
    pub gate_data: GateData,
    pub role_data: Vec<RoleData>,
}

#[derive(Debug)]
pub struct GateData {
    pub allow_rejoin: bool,
    pub gate_enabled: bool,
    pub key_role_id: u64,
    pub keyed_users: Vec<KeyedUser>,
}

#[derive(Debug)]
pub struct KeyedUser {
    pub user_id: u64,
    pub foreign_id: String,
    pub foreign_id_type: i32,
}

#[derive(Debug)]
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
            role.save(self.id, Some(false)).await?;
        }

        return Ok(());
    }

    pub async fn new(guild_arg: Option<&guild::Guild>, include_cleanup: Option<bool>) -> Self {
        // Start with a bland old object
        let mut guild: Guild = Guild {
            id: GuildId(0),
            welcome_message: String::from(""),
            gate_data: GateData {
                allow_rejoin: false,
                gate_enabled: false,
                key_role_id: 0,
                keyed_users: Vec::<KeyedUser>::new(),
            },
            role_data: Vec::<RoleData>::new(),
        };

        // Should we populate from the database?
        if guild_arg.is_some() {
            let found_guild = guild_arg.unwrap();
            guild.id = found_guild.id.clone();

            let pool = SQL_INSTANCE.lock().unwrap().pool.clone().unwrap();

            let guild_row_result: SqlxResult<MySqlRow> = sqlx::query::<sqlx::MySql>(
                "SELECT welcome_message, allow_rejoin, gate_enabled, key_role_id FROM guild WHERE id = ? LIMIT 1",
            )
            .bind(guild.id.as_u64().clone())
            .fetch_one(&pool)
            .await;

            // Gate Data
            if guild_row_result.is_ok() {
                let guild_row = guild_row_result.unwrap();
                guild.welcome_message = guild_row.get("welcome_message");
                guild.gate_data.allow_rejoin = guild_row.get("allow_rejoin");
                guild.gate_data.gate_enabled = guild_row.get("gate_enabled");
                guild.gate_data.key_role_id = guild_row.get("key_role_id");
            } else {
                // We hit an error (likely ResultNotFound).  Nothing really to do here, so we bail fast.
                return guild;
            }

            // Keyed Users
            let keyed_user_stream: SqlxResult<Vec<MySqlRow>> = sqlx::query::<sqlx::MySql>("SELECT * FROM keyed_users WHERE guild_id = ?")
                .bind(found_guild.id.as_u64().clone())
                .fetch_all(&pool)
                .await;

            if keyed_user_stream.is_ok() {
                for row in keyed_user_stream.unwrap().iter() {
                    guild.gate_data.keyed_users.push(KeyedUser {
                        user_id: row.get("user_id"),
                        foreign_id: row.get("foreign_id"),
                        foreign_id_type: row.get("foreign_id_type"),
                    })
                }
            }

            // Role Data
            // Import each existing role
            for role in found_guild.roles.values() {
                let new_role = RoleData::new(Some(&role)).await;
                guild.role_data.push(new_role);
            }

            if include_cleanup.is_some() && include_cleanup.unwrap() {
                // Get all the roles we have data on.
                let stream: SqlxResult<Vec<MySqlRow>> = sqlx::query::<sqlx::MySql>("SELECT role_id FROM role WHERE guild_id = ?")
                    .bind(found_guild.id.as_u64().clone())
                    .fetch_all(&pool)
                    .await;

                let mut stored_roles = Vec::<RoleId>::new();
                if stream.is_ok() {
                    let rows = stream.unwrap();
                    for row in rows.iter() {
                        stored_roles.push(RoleId(row.get("role_id")));
                    }
                }

                // Remove any known good roles (attached to the guild)
                for good_role in guild.role_data.iter() {
                    if let Some(pos) = stored_roles.iter().position(|x| *x == good_role.id) {
                        stored_roles.remove(pos);
                    }
                }

                // Anything left over should be deleted.
                for bad_role in stored_roles.iter() {
                    // Swallow the errors for now.
                    let _ = RoleData::delete(*bad_role).await;
                }
            }
        }

        return guild;
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
    pub async fn save(&self, guild_id: GuildId, skip_commanders_arg: Option<bool>) -> Result<(), Box<dyn Error>> {
        let skip_commanders = skip_commanders_arg.unwrap_or(false);

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

        if !skip_commanders && self.commanders.len() > 0 {
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

    pub async fn new(role_arg: Option<&guild::Role>) -> Self {
        let mut role: Self = Self {
            id: RoleId(0),
            can_join: false,
            name: String::from(""),
            commanders: Vec::<UserId>::new(),
        };

        if role_arg.is_some() {
            let found_role = role_arg.unwrap();
            role.id = found_role.id;
            role.name = found_role.name.clone();

            let pool = SQL_INSTANCE.lock().unwrap().pool.clone().unwrap();
            let mut should_save: bool = true;
            
            let row_result: SqlxResult<MySqlRow> =
                sqlx::query::<sqlx::MySql>("SELECT can_join, name FROM role WHERE guild_id = ? AND role_id = ? LIMIT 1")
                    .bind(found_role.guild_id.as_u64())
                    .bind(role.id.as_u64())
                    .fetch_one(&pool)
                    .await;

            if row_result.is_ok() {
                should_save = false;
            
                let row = row_result.unwrap();
                role.can_join = row.get("can_join");

                let stream: SqlxResult<Vec<MySqlRow>> = sqlx::query::<sqlx::MySql>("SELECT * FROM role_commanders WHERE role_id = ?")
                    .bind(found_role.id.as_u64().clone())
                    .fetch_all(&pool)
                    .await;

                if stream.is_ok() {
                    for row in stream.unwrap().iter() {
                        role.commanders.push(UserId(row.get("role_id")));
                    }
                }

                // If the name from the Guild API is different than the DB, we should update
                let old_name: String = row.get("name");
                if role.name != old_name {
                    should_save = true;
                }
            }

            if should_save {
                // Just swallow the errors here.
                let _ = role.save(found_role.guild_id, None).await;
            }
        }

        return role;
    }

    pub async fn delete(role_id: RoleId) -> Result<(), Box<dyn Error>> {
        let pool = SQL_INSTANCE.lock().unwrap().pool.clone().unwrap();

        sqlx::query::<sqlx::MySql>("DELETE FROM role_commanders WHERE role_id = ?")
            .bind(role_id.as_u64().clone())
            .execute(&pool)
            .await?;

        sqlx::query::<sqlx::MySql>("DELETE FROM role WHERE role_id = ?")
            .bind(role_id.as_u64().clone())
            .execute(&pool)
            .await?;

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

pub async fn import_guilds_from_file(buffer: &String) -> Result<(), Box<dyn std::error::Error>> {
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
