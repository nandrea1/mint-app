import requests
import json
import time

class MintService(object):
    username=''
    password=''
    session=''
    token = '';

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        data = {"username": self.username, "password": self.password, "task": "L", "nextPage": ""}
        response = self.session.post("https://wwws.mint.com/loginUserSubmit.xevent", data=data).text
        if "javascript-token" not in response.lower():
            raise Exception("Mint.com login failed")

        # 2: Grab token.
        tokensubind = response.lower().index('javascript-token')
        tokenstart = response.index('value', tokensubind)
        tokenstring = response[tokenstart:tokenstart+100]
        tokenquote1 = tokenstring.index('"')+1
        tokenquote2 = tokenstring.index('"', tokenquote1)
        self.token = tokenstring[tokenquote1:tokenquote2]
        print(self.token)

    def getAccounts(self):
        request_id = "115485" # magic number? random number?
        data = {"input": json.dumps([
        {"args": {
            "types": [
                "BANK", 
                "CREDIT", 
                "INVESTMENT", 
                "LOAN", 
                "MORTGAGE", 
                "OTHER_PROPERTY", 
                "REAL_ESTATE", 
                "VEHICLE", 
                "UNCLASSIFIED"
            ]
        }, 
        "id": request_id, 
        "service": "MintAccountService", 
        "task": "getAccountsSorted"}
        ])}

        response = self.session.post("https://wwws.mint.com/bundledServiceController.xevent?token="+self.token, data=data)
        response = json.loads(response.text)["response"]
        accounts = response[request_id]["response"]
        return accounts

    def refreshAccounts(self):
        request_id = "115485" # magic number? random number?
        data = {"token": self.token}

        response = self.session.post("https://wwws.mint.com/refreshFILogins.xevent", data=data)
        #response = json.loads(response.text)["response"]
       # accounts = response[request_id]["response"]
        updating = self.accountsUpdating()
        print(updating)
        loopcount =0
        while (updating):
            print('iteration ' + str(loopcount+1))
            if loopcount > 5:
                break
            time.sleep(2)
            updating = self.accountsUpdating();
            loopcount = loopcount + 1
        accounts = self.getAccounts()
        return accounts

    def accountsUpdating(self):
        request_id = "115485" # magic number? random number?
        data = {"input": json.dumps([
        {"args": {}, 
        "id": request_id, 
        "service": "MintFILoginService", 
        "task": "isUserFILoginRefreshing"}
        ])}

        response = self.session.post("https://wwws.mint.com/bundledServiceController.xevent?token="+self.token, data=data)
        response = json.loads(response.text)["response"]
        updating = response[request_id]["response"]
        return updating
