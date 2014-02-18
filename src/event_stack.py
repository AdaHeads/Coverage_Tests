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
    
    ws           = None
    messageStack = []
    ws_uri       = None
    authtoken    = None
    open         = False
    #messageStack = dict()
    
    def __init__(self, uri, token):
        super(EventListenerThread, self).__init__()
        self.ws_uri = uri
        self.authtoken = token
        self.messageStack = []
        self.open = False
    
    def stack_contains (self, event_type, call_id=None):
        for item in self.messageStack:
            if item['event'] == event_type:
                if call_id == None: 
                    return True
                elif item['call']['id'] == call_id:
                    return True
        return False

    def WaitFor (self, event_type, call_id=None, timeout=10.0):
        RESOLUTION = 0.5
        timeSlept = 0.0;
        while timeSlept < timeout:
            timeSlept += RESOLUTION
            if self.stack_contains (event_type=event_type, call_id=call_id):
                return;
            sleep (RESOLUTION)
        raise TimeOutReached (event_type + ":" + str (call_id))
    
    def getLatestEvent (self, event_type, call_id):
        for item in self.messageStack.reverse():
            if item['event'] == event_type and item['call']['id'] == call_id:
                return item['event']
        return False

    def dump_stack(self):
        return pformat(self.messageStack)
    
    def on_error(self, ws, error):
        logging.error (error)

    def on_open (self, ws):
        logging.info ("Opened websocket")
        self.open = True

    def on_close(self, ws):
        logging.info ("Closed websocket")
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
            logging.critical("Websocket connected to " + full_uri)
        except:
            logging.critical("Websocket could not connect to " + full_uri)
    
    def run(self):
        try:
            logging.info ("Starting websocket")
            self.connect()
            self.ws.run_forever()
        except:
            logging.critical("Run in thread failed!")
            
    def stop(self):
        logging.info ("stopping websocket")
        if self.open:
            self.ws.close();
        
if __name__ == "__main__":

    elt = EventListenerThread(uri=config.call_flow_events, token=config.authtoken)
    elt.start();        
