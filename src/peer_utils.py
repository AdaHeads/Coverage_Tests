import json

class PeerList ():
    
    __JSONlist = dict()

    def fromJSON (self, s):
        self.__JSONlist = json.loads(s)
        return self
        
    def locatePeer (self, peer_id):
        foundPeer = None
        for peer in self.__JSONlist['peers']:
            if peer_id in peer:
                foundPeer = peer 
        return foundPeer
        
