import os
import json

class UserDataSource(object):

    DATA_STORE = "userdata"

    def saveUserState(self, user, state):
        if not os.path.isdir(self.DATA_STORE):
            os.mkdir(self.DATA_STORE)

        filePath = self.DATA_STORE + "/" + user
        with os.open(filePath, "rw") as userData:
            data = json.loads(userData.read)
            data[state['date']] = state

    def loadUserState(self, user):
        if not os.path.isdir(self.DATA_STORE):
            os.mkdir(self.DATA_STORE)

        filePath = self.DATA_STORE + "/" + user
        if not os.path.exists(filePath):
            os.write(filePath, "{}")

        with os.open(self.DATA_STORE + "/" + user) as userData:
            data = json.loads(userData.read)
