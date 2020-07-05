from typing import Dict, List

import discord


class ServerGateData:
    def __init__(self, gate_enabled=False, allow_rejoin=False, key_role_id=0, keyed_users: Dict[int, int] = {}):
        self.gate_enabled = gate_enabled
        self.allow_rejoin = allow_rejoin
        self.key_role_id = key_role_id
        self.keyed_users = keyed_users


class ServerRoleData:
    def __init__(self, id: int, name: str, can_join=False, commanders: List[int] = {}):
        self.id = id
        self.name = name
        self.can_join = can_join
        self.commanders = commanders

    @classmethod
    def from_discord_role(cls, role: discord.Role):
        return cls(role.id, role.name)


class ServerData:
    def __init__(self, id: int, name: str, greeting_message="", gate_data=ServerGateData(), role_data: Dict[int, ServerRoleData] = {}):
        self.id = id
        self.name = name
        self.greeting_message = greeting_message
        self.gate_data = gate_data
        self.role_data = role_data

    @classmethod
    def from_discord_guild(cls, guild: discord.Guild):
        return cls(guild.id, guild.name, "", ServerGateData(), {})

ConfigData = Dict[int, ServerData]