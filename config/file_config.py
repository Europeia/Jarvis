import inspect
import json
from typing import Dict, List

from .config_manager import BaseConfigManager
from .config_model import (ConfigData, ServerData, ServerGateData,
                           ServerRoleData)


class ServerGateDataFile(ServerGateData):
    @classmethod
    def from_json(cls, data: dict):
        # Data might be in the old format
        gate_enabled = data["gateEnabled"] if data.get(
            "gateEnabled") is not None else data.get("gate_enabled")
        allow_rejoin = data["allowRejoin"] if data.get(
            "allowRejoin") is not None else data.get("allow_rejoin")
        key_role_id = data["keyRoleId"] if data.get(
            "keyRoleId") is not None else data.get("key_role_id")
        if key_role_id == "" or key_role_id is None:
            key_role_id = "0"
        keyed_users: Dict[str, str] = data["keyedUsers"] if data.get(
            "keyedUsers") is not None else data.get("keyed_users")

        return cls(bool(gate_enabled), bool(allow_rejoin), int(key_role_id), keyed_users)

    # def to_json(self):
    #     obj_json = dict()
    #     obj_json['allow_rejoin'] = self.allow_rejoin
    #     obj_json['gate_enabled'] = self.gate_enabled
    #     obj_json['key_role_id'] = self.key_role_id
    #     obj_json['keyed_users'] = self.keyed_users


class ServerRoleDataFile(ServerRoleData):
    @classmethod
    def from_json(cls, id: int, data: dict):
        # Data might be in the old format
        can_join = data["canJoin"] if data.get(
            "canJoin") is not None else data.get("can_join")

        commanders: List[int] = []
        if isinstance(data["commanders"], list):
            commanders = data["commanders"]
        elif isinstance(data["commanders"], dict):
            for key in data["commanders"].keys():
                if int(key) > 0:
                    commanders.append(int(key))

        return cls(id, data["name"], bool(can_join), commanders)

    @classmethod
    def from_json_list(cls, data: dict) -> Dict[int, ServerRoleData]:
        roles = {}
        for key in data.keys():
            if isinstance(key, int):
                id = key
            elif isinstance(key, str) and key.isdigit():
                id = int(str(key))
            else:
                continue

            value = data[key]
            roles.update({id: cls.from_json(id, value)})

        return roles


class ServerDataFile(ServerData):
    @ classmethod
    def from_json(cls, id, data: dict):
        # Data might be in the old format.
        greeting_message = data["greetingMessage"] if data.get(
            "greetingMessage") is not None else data.get("greeting_message")
        gate_data = data["gateData"] if data.get(
            "gateData") is not None else data.get("gate_data")
        role_data = data["roleData"] if data.get(
            "roleData") is not None else data.get("role_data")

        return cls(id, str(data["name"]), str(greeting_message), ServerGateDataFile.from_json(gate_data), ServerRoleDataFile.from_json_list(role_data))

    @classmethod
    def from_json_list(cls, data: dict) -> Dict[int, ServerData]:
        servers = {}
        for key in data.keys():
            if isinstance(key, int):
                id = key
            elif isinstance(key, str) and key.isdigit():
                id = int(str(key))
            else:
                continue
            value = data[key]
            servers.update({id: ServerDataFile.from_json(id, value)})
        return servers


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("_")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj


class FileConfigManager(BaseConfigManager):
    def readConfig(self):
        try:
            f = open('data/config.json', 'w+')
            servers = ServerDataFile.from_json_list(json.load(f))
            self.config_data: ConfigData = {
                server_id: servers[server_id] for server_id in servers.keys()}
        except Exception as ex:
            self.config_data: ConfigData = {}

        return

    def writeConfig(self):
        f = open('data/config.json',  'w+')

        json.dump(self.config_data, f, cls=ObjectEncoder, indent=2)
