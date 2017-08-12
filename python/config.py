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
        for iRole in range(len(server.roles)):
            role = server.roles[iRole]
            if not role.is_default():
                roleData = serverData['roleData'][str(role.id)] if serverData['roleData'].get(str(role.id)) is not None else {}
                roleData['name'] = role.name
                roleData['commanders'] = roleData['commanders'] if roleData.get('commanders') is not None else {}
                for memberId in roleData['commanders']:
                    member = server.get_member(int(memberId))
                    if member is not None:
                        roleData['commanders'][memberId] = self.__formatMemberName(member)
                serverData['roleData'][str(role.id)] = roleData
        self.configData[str(server.id)] = serverData
    
    def addCommander(self,  server: discord.Guild,  role: discord.Role,  member: discord.Member):
        serverData = self.configData.get(str(server.id))
        if serverData is not None:
            roleData = serverData['roleData'].get(str(role.id))
            if roleData is not None:
                roleData['commanders'][str(member.id)] = self.__formatMemberName(member)
    
    def remCommander(self,  server: discord.Guild,  role: discord.Role,  member: discord.Member):
        if self.isCommander(server,  role,  member):
            del self.configData[str(server.id)]['roleData'][str(role.id)][str(member.id)]
    
    def isCommander(self,  server: discord.Guild,  role: discord.Role,  member: discord.Member):
        serverData = self.configData.get(str(server.id))
        if serverData is not None:
            roleData = serverData['roleData'].get(str(role.id))
            if roleData is not None:
                commander = roleData.get(str(member.id))
                if commander is not None:
                    return True
        return False

    #Utility Functions      
    def __formatMemberName(self,  member: discord.Member):
        return member.name + '@#' + member.discriminator
