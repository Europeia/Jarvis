pub struct Guild {
    id: GuildId,
    welcome_message: String;
    gate_data: GateData;
}

pub struct GateData {
    allow_rejoin: bool,
    gate_enabled: bool,
    key_role_id: u64,
    keyed_users: KeyedUser[]
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
