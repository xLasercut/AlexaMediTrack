import os
import json

class SpineProxy(object):
    DOSAGE_KEY = "dosage"
    COURSE_KEY = "course"
    NAME_KEY = "name"
    MEDICATION_KEY = "medication"

class FakeSpineProxy(SpineProxy):

    FAKE_DATA_SOURCE = "fakespinedata.json"

    def __init__(self):
        self.dataSource = self._loadData()

    def _loadData(self):
        dataSource = {}
        with os.open(self.FAKE_DATA_SOURCE,"r") as source:
            dataSource = json.loads(source.read)

        return dataSource

    def getPrescriptions(self, nhsNumber):
        """ Gets all prescriptions from spine """
        return self.dataSource.get(nhsNumber)

