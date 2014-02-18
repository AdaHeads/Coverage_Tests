import config
import logging

from subprocess import Popen, PIPE

class Dial_Failed(Exception):
    pass

class Process_Failure(Exception):
    pass

class SipAccount():
    
    username  = None
    password  = None
    server    = None
    sip_port  = None 
    
    def __init__(self, username, password, server=config.pbx, sip_port=5060):
        self.username  = username
        self.password  = password
        self.server    = server
        self.sip_port  = str (sip_port)  # This should probably be kept as int, by we really don't need the int further along the way.
        
    def toString(self):
        return self.username + "@" + self.server + ":" + self.sip_port

class SipAgent:
    
    account    = None
    binaryPath = None
    __process  = None
    
    def __init__ (self, account, binaryPath=config.sip_binary_path):
        self.account    = account
        self.binaryPath = binaryPath

    def Connect(self):
        try:
            self.__process = Popen([self.binaryPath, 
                                    self.account.username, 
                                    self.account.password, 
                                    self.account.server, 
                                    self.account.sip_port],
                                   stdin=PIPE,
                                   stdout=PIPE)
        except:
            logging.fatal("Process spawinging failed, check path! ")
            raise Process_Failure (self.binaryPath) 
                
        # Waint for the account to become ready.
        self.__waitFor("+READY")
        logging.info("SIP agent " + self.account.toString() + " is ready.");
            
        return self
    
    def Dial (self, extension, server=None):
        if server == None:
            server = self.account.server

        self.__process.stdin.write("dsip:"+extension+ "@" + server + "\n")
        self.__waitFor("+OK")
        logging.info("Dialing " + extension+ "@" + server);
                
    def HangupAllCalls(self):
        self.__process.stdin.write("h\n"); # Hangup
        self.__waitFor("+OK")

    def Wait_For_Dialtone(self):
        self.__waitFor("+dialtone")

    def QuitProcess(self):
        self.__process.stdin.write("q\n"); # Quit
        self.__waitFor("+OK")
        self.__process.wait()
    
    def __waitFor(self, expectedLine):
        got_reply = False
        while not got_reply:
            line = self.__process.stdout.readline()
            if expectedLine in line:
                got_reply = True                
            elif "-ERROR" in line:
                raise Process_Failure ("Process returned:" + line) 
        