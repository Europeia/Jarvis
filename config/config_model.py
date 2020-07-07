from typing import Dict, List

import discord


class ServerGateData:
    @property
    def gate_enabled(self) -> bool:
        return self._gate_enabled

    @gate_enabled.setter
    def gate_enabled(self, value: bool):
        self._gate_enabled = value

    @property
    def allow_rejoin(self) -> bool:
        return self._allow_rejoin

    @allow_rejoin.setter
    def allow_rejoin(self, value: bool):
        self._allow_rejoin = value

    @property
    def key_role_id(self) -> int:
        return self._key_role_id

    @key_role_id.setter
    def key_role_id(self, value: int):
        self._key_role_id = value

    @property
    def keyed_users(self) -> Dict[int, int]:
        return self._keyed_users

    @keyed_users.setter
    def keyed_users(self, value: Dict[int, int]):
        self._keyed_users = value

    def __init__(self, gate_enabled=False, allow_rejoin=False, key_role_id=0, keyed_users: Dict[int, int] = {}):
        self.gate_enabled = gate_enabled
        self.allow_rejoin = allow_rejoin
        self.key_role_id = key_role_id
        self.keyed_users = keyed_users


class ServerRoleData:
    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def can_join(self) -> bool:
        return self._can_join

    @can_join.setter
    def can_join(self, value: bool):
        self._can_join = value

    @property
    def commanders(self) -> List[int]:
        return self._commanders

    @commanders.setter
    def commanders(self, value: List[int]):
        self._commanders = value

    def __init__(self, id: int, name: str, can_join=False, commanders: List[int] = []):
        self.id = id
        self.name = name
        self.can_join = can_join
        self.commanders = commanders

    @classmethod
    def from_discord_role(cls, role: discord.Role):
        return cls(role.id, role.name)


class ServerData:
    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def greeting_message(self) -> str:
        return self._greeting_message

    @greeting_message.setter
    def greeting_message(self, value: str):
        self._greeting_message = value

    @property
    def gate_data(self) -> ServerGateData:
        return self._gate_data

    @gate_data.setter
    def gate_data(self, value: ServerGateData):
        self._gate_data = value

    @property
    def role_data(self) -> ServerRoleData:
        return self._role_data

    @role_data.setter
    def role_data(self, value: ServerRoleData):
        self._role_data = value

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
