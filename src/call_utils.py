import json

class NotFound(Exception):
    pass

class CallList ():

    __JSONlist = dict()

    def fromJSON (self, s):
        self.__JSONlist = json.loads(s)
        return self

    def Empty(self):
        return self.NumberOfCalls() == 0

    def NumberOfCalls(self):
        if 'calls' in self.__JSONlist:
            return len(self.__JSONlist['calls'])

    def toString(self):
        return self.to_string()

    def to_string(self):
        return json.dumps(self.__JSONlist)

    def Calls(self):
        return self.__JSONlist['calls']

    def locateCall (self, call_id):
        for call in self.__JSONlist['calls']:
            if call['id'] == call_id:
                return call
        raise NotFound



