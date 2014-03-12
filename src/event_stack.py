
import websocket
import logging
import json
import config
import threading
from time import sleep
from pprint import pformat

class TimeOutReached(Exception):
    pass

class EventListenerThread(threading.Thread):

    log          = None
    ws           = None
    messageStack = []
    ws_uri       = None
    authtoken    = None
    open         = False
    #messageStack = dict()

    def __init__(self, uri, token):
        self.log = self.log = logging.getLogger(self.__class__.__name__)
        super(EventListenerThread, self).__init__()
        self.ws_uri = uri
        self.authtoken = token
        self.open = False
        self.flush()

    def flush(self):
        self.messageStack = []

    def stack_contains (self, event_type, call_id=None, destination=None):
        for item in self.messageStack:
            if item['event'] == event_type:
                if call_id is None:
                    if destination is None:
                        return True
                    elif item['call']['destination'] == destination:
                        return True
                elif item['call']['id'] == call_id:
                    if destination == None:
                        return True
                    elif item['call']['destination'] == destination:
                        return True
        return False

    def WaitForOpen (self, timeout=3.0):
        RESOLUTION = 0.1
        timeSlept = 0.0
        while timeSlept < timeout:
            timeSlept += RESOLUTION
            if self.open:

                return
            sleep (RESOLUTION)
        raise TimeOutReached ("Did not open websocket in a timely manner")

    def WaitFor (self, event_type, call_id=None, timeout=10.0):
        RESOLUTION = 0.1
        timeSlept = 0.0
        while timeSlept < timeout:
            timeSlept += RESOLUTION
            if self.stack_contains (event_type=event_type, call_id=call_id):
                return
            sleep (RESOLUTION)
        raise TimeOutReached (event_type + ":" + str (call_id))

    def getLatestEvent (self, event_type, call_id=None, destination=None):
        for item in reversed (self.messageStack):
            if item['event'] == event_type:
                if call_id == None:
                    if destination == None:
                        return item['event']
                    elif item['call']['destination'] == destination:
                        return item['event']
                elif item['call']['id'] == call_id:
                    if destination == None:
                        return item['event']
                    elif item['call']['destination'] == destination:
                        return item['event']
        return False

    def Get_Latest_Event (self, Event_Type, Call_ID = None, Destination = None):
        try:
            for item in reversed (self.messageStack):
                if item['event'] == Event_Type:
                    if Call_ID is None:
                        if Destination is None:
                            return item
                        elif item['call']['destination'] == Destination:
                            return item
                    elif item['call']['id'] == Call_ID:
                        if Destination is None:
                            return item
                        elif item['call']['destination'] == Destination:
                            return item
        except:
            self.log.critical ("Exception in Get_Latest_Event: messageStack = " + str (self.messageStack))
            raise

        self.log.info ("Didn't find a match on {Event_Type = " + Event_Type + " & Call_ID = " + str(Call_ID) + " & Destination = " + str(Destination) + "}")
        return None

    def dump_stack(self):
        return pformat(self.messageStack)

    def on_error(self, ws, error):
        self.log.error ("Unspecified error:" + str(error))

    def on_open (self, ws):
        self.log.info ("Opened websocket")
        self.open = True

    def on_close(self, ws):
        self.log.info ("Closed websocket")
        self.open = False

    def on_message(self, ws, message):
        self.messageStack.append(json.loads(message)['notification'])

    def connect (self):
        full_uri= self.ws_uri +  "?token=" + self.authtoken
        try:
            self.ws = websocket.WebSocketApp (full_uri,
                                              on_message = self.on_message,
                                              on_error = self.on_error,
                                              on_close = self.on_close)
            self.ws.on_open = self.on_open
            self.log.info("Websocket connected to " + full_uri)
        except:
            self.log.critical("Websocket could not connect to " + full_uri)

    def run(self):
        try:
            self.log.info ("Starting websocket")
            self.connect()
            self.ws.run_forever()
        except:
            self.log.critical("Run in thread failed!")

    def stop(self):
        if self.open:
            self.ws.close()
            self.open = False

    def __del__(self):
        self.stop()
        
        
if __name__ == "__main__":

    elt = EventListenerThread(uri=config.call_flow_events, token=config.authtoken)
    elt.start()
    elt.stop()
