import json

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
        return json.dumps(self.__JSONlist)
        
    def locateCall (self, call_id):
        foundCall = None
        for call in self.__JSONlist['calls']:
            if call_id in call:
                foundCall = call 
        return foundCall
        
