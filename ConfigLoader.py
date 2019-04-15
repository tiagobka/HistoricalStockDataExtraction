import json

class APIaccount:
    def __init__(self, API, account, key, email, limits):
        self.API = API
        self.account = account
        self.key = key
        self.email = email
        self.limits = limits
    def __str__(self):
        str = "API: %s\n"%(self.API)
        str += "Account: %s\n"%(self.account)
        str += "Key: %s\n" % (self.key)
        str += "Email: %s\n" % (self.email)
        str += "API Call Limits: {\n"
        for i in self.limits:
            str += i
            str+= ":" + self.limits[i] + "\n"
        str += "}"
        return str


class configImport:
    def __init__(self, configFile):
        self.config = self.loadConfig(configFile)
        self.APIs = self.getAPIs()

    def loadConfig(self, file):
        with open(file, 'r') as f:
            config = json.load(f)
        return config

    def getAPIs (self):
        api = self.config["API"]
        listOfAccounts = []
        for i in api:
            for j in api[i]:
                acctCfg = api[i][j]
                newAcct = APIaccount(i, j, acctCfg["Key"], acctCfg["Email"], acctCfg["Limits"])
                listOfAccounts.append(newAcct)
        return listOfAccounts


    def getAccountsByAPI(self,API):
        acct = []
        for i in self.APIs:
            if i.API == API:
                acct.append(i)
        return acct


    def getAPIKey(self,API):
        keys = []
        for i in self.APIs:
            if i.API == API:
                keys.append(i.key)
        if len(keys) == 1:
            return keys[0]
        return keys


#cnf = configImport("config")
#print (cnf.APIs[0].key)

