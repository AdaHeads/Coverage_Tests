import config
import logging
import time

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
        
    def to_string(self):
        return self.username + "@" + self.server + ":" + self.sip_port

#TODO: Throttle the rate of commands being sent per second, as the SIP process tends to choke on them.
class SipAgent:
    
    log        = None
    account    = None
    binaryPath = None
    __process  = None

    def __init__ (self, account, binaryPath=config.sip_binary_path):
        self.log = logging.getLogger(self.__class__.__name__)
        self.account    = account
        self.binaryPath = binaryPath

    def Connected(self):
        return not self.__process is None

    def Connect(self):
        if not self.Connected():
            try:
                self.__process = Popen([self.binaryPath,
                                        self.account.username,
                                        self.account.password,
                                        self.account.server,
                                        self.account.sip_port],
                                       stdin=PIPE,
                                       stdout=PIPE)
            except:
                self.log.fatal("Process spawinging failed, check path! ")
                raise Process_Failure (self.binaryPath)

            # Waint for the account to become ready.
            self.__waitFor("+READY")

        return self
    
    def Dial (self, extension, server=None):
        if server == None:
            server = self.account.server

        self.__process.stdin.write("dsip:"+extension+ "@" + server + "\n")
        self.__waitFor("+OK")
        self.log.info("Dialing " + extension+ "@" + server);

    def Unregister (self):
        self.__process.stdin.write("u\n");
        self.__waitFor("+OK")
        self.log.info("SIP agent " + self.account.to_string() + " unregistered.");
        time.sleep(0.05) # Let the unregistration settle.

    def Register (self):
        self.__process.stdin.write("r\n");
        self.__waitFor("+OK")
        self.log.info("SIP agent " + self.account.to_string() + " registered.");

    def HangupAllCalls(self):
        self.__process.stdin.write("h\n");
        self.__waitFor("+OK")

    def enable_auto_answer(self):
        self.__process.stdin.write("a\n");
        self.__waitFor("+OK")

    def disable_auto_answer(self):
        self.__process.stdin.write("m\n");
        self.__waitFor("+OK")

    def pickup_call(self):
        self.__process.stdin.write("p\n");
        self.__waitFor("+OK")

    def wait_for_call(self):
        self.__waitFor("+CALL")

    def sip_uri(self):
        return "sip:" + self.account.to_string ()

    def Wait_For_Dialtone(self):
        #self.__waitFor("+dialtone")
        self.log.info("Should have been waiting for a dial-tone here.  TODO: Fix 'sip_utils.py'.")

    def QuitProcess(self):
        self.HangupAllCalls()
        self.__process.stdin.write("q\n"); # Quit
        self.__waitFor("+OK")
        try:
            self.__process.wait()
        except AttributeError: # Process is already closed.
            pass
    
    def __waitFor(self, expectedLine):
        got_reply = False
        while not got_reply:
            line = self.__process.stdout.readline()
            if expectedLine in line:
                got_reply = True
            elif "-ERROR" in line:
                raise Process_Failure ("Process returned:" + line) 
            elif line == "":
                raise Process_Failure ("Process returned empty line, which " + \
                                       "indicates an internal failure in the SIP process. " + \
                                       "Inserting delays between Register/Unregister calls remedies it.")
            else:
                logging.info ("Process returned:" + line) 

    def __send(self, command):
        self.__process.stdin.write(command + "\n");
        got_reply = False

if __name__ == "__main__":

    agent = SipAgent(account=SipAccount(username="1100",
                                        password="1234",
                                        sip_port=6060))
    agent.Connect()

    agent.Register()
    time.sleep(0.05)
    agent.Unregister()
    time.sleep(0.05)
    agent.Register()
