import discord
import json

class ConfigManager:
    configData = None
    
    def __init__(self):
        self.readConfig()
        
    #IO Operations
    def readConfig(self):
        try:
            f = open('data/config.json')
            self.configData = json.load(f)
        except:
            self.configData = {}
        
    def writeConfig(self):
        f = open('data/config.json',  'w')
        json.dump(self.configData, f, indent=2)
        
    #DB Manipulation        
    def updateServerData(self, server: discord.Guild):
        serverData = self.configData[str(server.id)] if self.configData.get(str(server.id)) is not None else {}
        serverData['name'] = server.name
        self.configData[str(server.id)] = serverData
        self.__updateRolesData(server)
        
    def __updateRolesData(self,  server: discord.Guild):
        serverData = self.configData[str(server.id)]
        serverData['roleData'] = serverData['roleData'] if serverData.get('roleData') is not None else {}
        newServerData = {}
        newServerData['roleData'] = {}
        for iRole in range(len(server.roles)):
            role = server.roles[iRole]
            if not role.is_default():
                roleData = serverData['roleData'][str(role.id)] if serverData['roleData'].get(str(role.id)) is not None else {}
                newRoleData = {}
                newRoleData['name'] = role.name
                newRoleData['commanders'] = roleData['commanders'] if roleData.get('commanders') is not None else {}
                for memberId in newRoleData['commanders']:
                    member = server.get_member(int(memberId))
                    if member is not None:
                        newRoleData['commanders'][memberId] = self.__formatMemberName(member)
                newServerData['roleData'][str(role.id)] = newRoleData
        self.configData[str(server.id)] = newServerData
    
    def addCommander(self,  server: discord.Guild,  role: discord.Role,  member: discord.Member):
        commanderList = self.__getCommanderList(self.__getRole(self.__getRoleList(self.configData.get(str(server.id))), str(role.id)))
        if commanderList is not None:
            commanderList[str(member.id)] = self.__formatMemberName(member)
    
    def remCommander(self,  server: discord.Guild,  role: discord.Role,  member: discord.Member):
        if self.isCommander(server,  role,  member):
            del self.configData[str(server.id)]['roleData'][str(role.id)]['commanders'][str(member.id)]
    
    def listCommanders(self,  server: discord.Guild,  role: discord.Role):
        output = ''
        commanderList = self.__getCommanderList(self.__getRole(self.__getRoleList(self.configData.get(str(server.id))), str(role.id)))
        for commander in commanderList:
            output += commanderList[commander] + '\n'
        return output;
    
    def isCommander(self,  server: discord.Guild,  role: discord.Role,  member: discord.Member):
        commander = self.__getCommander(self.__getCommanderList(self.__getRole(self.__getRoleList(self.configData.get(str(server.id))), str(role.id))), str(member.id))
        if commander is not None:
            return True
        return False
    
    #Private Model Utility Functions
    def __getCommander(self, commanderList,  commanderId):
        if commanderList is not None and len(commanderList) > 0:
            return commanderList.get(commanderId)
        return None
    
    def __getCommanderList(self, roleData):
        if roleData is not None:
            return roleData.get('commanders')
        return None
    
    def __getRole(self, roleList, roleId):
        if roleList is not None and len(roleList) > 0:
            return roleList.get(roleId)
        return None
    
    def __getRoleList(self, serverData):
        if serverData is not None:
            return serverData.get('roleData')
        return None
    

    #Utility Functions      
    def __formatMemberName(self,  member: discord.Member):
        return member.name + '@#' + member.discriminator
