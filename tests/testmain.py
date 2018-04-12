import unittest
import main
from pystache import render
import shutil
import os
from datetime import datetime

class MainTests(unittest.TestCase):

    def test_getUserDataWhenExists(self):
        userId = "someUserId"
        self._setupSource(datetime.now().strftime("%Y%m%d"), userId)

        data = main.getUserData(userId)
        self.assertEquals(data.userId, userId)

    def test_getUserDataWhenNew(self):
        userId = "someUserId"
        data = main.getUserData(userId)
        self.assertEquals(data.userId, userId)

    TEST_DATA_FILE = "testuserdatatemplate.json"
    SAVE_FOLDER = "userdata"

    def _setupSource(self, date, userId):
        data = None
        target = os.path.join(self.SAVE_FOLDER,  userId + ".json")
        with open(self.TEST_DATA_FILE, "r") as file:
            data = file.read()

        data = render(data, {"date" : date, "userId" : userId})

        with open(target, "w") as file:
            file.write(data)

    def setUp(self):
        if not os.path.isdir(self.SAVE_FOLDER):
            os.mkdir(self.SAVE_FOLDER)

    def tearDown(self):
        if os.path.isdir(self.SAVE_FOLDER):
            shutil.rmtree(self.SAVE_FOLDER)

if __name__ == '__main__':
    unittest.main()
