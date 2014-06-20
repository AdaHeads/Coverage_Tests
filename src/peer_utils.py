import json

class NotFoundError(Exception):
    pass

class PeerList ():

    __JSONlist = dict()

    def fromJSON (self, s):
        self.__JSONlist = json.loads(s)
        return self

    def locatePeer (self, peer_id):
        """Locates the peer with the supplied id in the instance.
        :param peer_id: The id of the peer to locate.
        :return
        """
        for peer in self.__JSONlist['peers']:
            if peer['userid'] == peer_id:
                return peer
        raise NotFoundError()
        
