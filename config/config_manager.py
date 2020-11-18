from typing import Dict, List
from abc import ABCMeta, abstractmethod

import discord

from .config_model import ServerData, ServerRoleData, ServerGateData, ConfigData


class BaseConfigManager(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.config_data: ConfigData = dict()
        self.readConfig()

    @abstractmethod
    def readConfig(self):
        raise NotImplementedError(
            "readConfig not implemented on base ConfigManager")

    @abstractmethod
    def writeConfig(self):
        raise NotImplementedError(
            "writeConfig not implemented on base ConfigManager")

    def updateServerData(self, guild: discord.Guild):
        server_data = self.config_data[guild.id] if self.config_data.get(
            guild.id) is not None else ServerData.from_discord_guild(guild)
        server_data.name = guild.name
        self.config_data[guild.id] = server_data
        # __update_roles_data_from_discord updates the DB, so we don't need to.
        self.__update_roles_data_from_discord(guild)

    def __update_roles_data_from_discord(self, guild: discord.Guild):
        new_roles_data: Dict[int, ServerRoleData] = {}

        server_data = self.config_data[guild.id] if self.config_data.get(
            guild.id) is not None else ServerData.from_discord_guild(guild)

        for iRole in range(len(guild.roles)):
            role = guild.roles[iRole]
            if not role.is_default():
                # Get the Role Data from memory
                old_role_data = server_data.role_data[role.id] if server_data.role_data.get(
                    role.id) is not None else ServerRoleData.from_discord_role(role)

                # Create new Role data with updated ID and Name from Discord
                new_role_data = ServerRoleData(
                    role.id, role.name, old_role_data.can_join, old_role_data.commanders)

                # Strip out any commanders that are no longer part of the server.
                new_commanders: List[int] = []

                for commander in new_role_data.commanders:
                    if guild.get_member(commander) is not None:
                        new_commanders.append(commander)

                new_role_data.commanders = new_commanders

                new_roles_data[role.id] = new_role_data

        # Replace server data in memory
        server_data.role_data = new_roles_data
        self.config_data[server_data.id] = server_data

        # Write to DB
        self.writeConfig()

    # Commanders
    def addCommander(self, guild: discord.Guild, role: discord.Role, member: discord.Member):
        _server = self.config_data[guild.id] if self.config_data.get(
            guild.id) is not None else ServerData.from_discord_guild(guild)

        _role = _server.role_data[role.id] if _server.role_data.get(
            role.id) is not None else ServerRoleData.from_discord_role(role)
        _server.role_data[role.id] = _role

        if member.id not in _role.commanders:
            _role.commanders.append(member.id)

        self.writeConfig()

    def remCommander(self, guild: discord.Guild, role: discord.Role, member: discord.Member):
        _server = self.config_data[guild.id] if self.config_data.get(
            guild.id) is not None else ServerData.from_discord_guild(guild)

        _role = _server.role_data[role.id] if _server.role_data.get(
            role.id) is not None else ServerRoleData.from_discord_role(role)
        _server.role_data[role.id] = _role

        while member.id in _role.commanders:
            _role.commanders.remove(member.id)

        self.writeConfig()

    def listCommanders(self, guild: discord.Guild, role: discord.Role) -> str:
        _server = self.config_data[guild.id] if self.config_data.get(
            guild.id) is not None else ServerData.from_discord_guild(guild)

        _role = _server.role_data[role.id] if _server.role_data.get(
            role.id) is not None else ServerRoleData.from_discord_role(role)

        output = ''

        for commander in _role.commanders:
            output += str(commander) + ": "
            member = guild.get_member(commander)
            if member is None:
                output += "Unknown"
            else:
                output += self.__formatMemberName(member)
            output += "\n"

        return output

    def isCommander(self, guild: discord.Guild, role: discord.Role, member: discord.Member) -> bool:
        _server = self.config_data[guild.id] if self.config_data.get(
            guild.id) is not None else ServerData.from_discord_guild(guild)

        _role = _server.role_data[role.id] if _server.role_data.get(
            role.id) is not None else ServerRoleData.from_discord_role(role)

        return member.id in _role.commanders

    # Greetings
    def setGreetingMessage(self, guild: discord.Guild, greeting_message: str):
        self.config_data[guild.id].greeting_message = greeting_message

    def getGreetingMessage(self, guild: discord.Guild) -> str:
        old_message = self.config_data[guild.id].greeting_message
        if old_message == '':
            return None
        else:
            return old_message

    # Joinable Roles
    def setJoinableRole(self, guild: discord.Guild, role: discord.Role, joinable: bool):
        self.__update_roles_data_from_discord(guild)

        self.config_data[guild.id].role_data[role.id].can_join = joinable

        self.writeConfig()

    def getJoinableRoles(self, guild: discord.Guild) -> List[int]:
        self.__update_roles_data_from_discord(guild)
        roles: List[int] = []

        for role_id in self.config_data[guild.id].role_data.keys():
            if self.config_data[guild.id].role_data[role_id].can_join:
                roles.append(role_id)

        return roles

    def isJoinableRole(self, guild: discord.Guild, role: discord.Role) -> bool:
        return role.id in self.getJoinableRoles(guild)

    # Server Gating
    def getGateData(self, guild: discord.Guild):
        if self.config_data[guild.id] is not None:
            return self.config_data[guild.id].gate_data
        else:
            return ServerGateData()

    def setGateData(self, guild: discord.Guild, gateEnabled: bool, allowRejoin: bool, keyRoleId: str, keyedUsers: Dict[int, int]):
        server_data = self.config_data[guild.id] if self.config_data[guild.id] is not None else ServerData.from_discord_guild(
            guild)

        server_data.gate_data = ServerGateData(
            gateEnabled, allowRejoin, keyRoleId, keyedUsers)
        self.config_data[guild.id] = server_data
        self.writeConfig()

    # Utility Functions
    def __formatMemberName(self, member: discord.Member):
        return member.name + '@#' + member.discriminator
