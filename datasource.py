import os
import json
from datetime import datetime

class UserDataSource(object):

    DATA_STORE = "userdata"

    def save(self, userId, state):
        self._makeSureFolderExists()

        # Open the datasourse if it exists.
        data = self.load(userId)
        if not data:
            data = {}

        # Update the data
        data[state['date']] = state

        # Write changes
        filePath = self._getFilePath(userId)
        dataString = json.dumps(data)
        with open(filePath, "w") as userData:
            userData.write(dataString)

    def load(self, userId):
        self._makeSureFolderExists()

        # Open file
        filePath = self._getFilePath(userId)
        if not os.path.exists(filePath):
            return None

        # Load state
        data = None
        date = datetime.now().strftime("%Y%m%d")
        with open(filePath, "r") as userData:
            data = userData.read()

        data = json.loads(data)
        data = data.get(date)

        return data

    def _makeSureFolderExists(self):
        if not os.path.isdir(self.DATA_STORE):
            os.mkdir(self.DATA_STORE)

    def _getFilePath(self, userId):
        return self.DATA_STORE + "/" + userId + '.json'


class UserIdMapping(object):

    def getNhsNumberFromUserId(self, userId):
        """ TODO ADD LOGIC """
        return "9999123456"
