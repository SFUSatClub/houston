""" Command class
- maintains an internal represenation of the command as a dict, since that's required for Kivy Recycleviews
- using a class makes it easier for us to add command data fields ish ... 
- we also do validation of the inputs automatically
"""

class Command():
    def __init__(self, cmdid, cmd, epoch, timeout, expect, rel):
        self.cmdid = cmdid 
        self.cmd = cmd
        self.epoch = epoch
        self.timeout = timeout
        self.expect = expect
        self.rel = rel

        self.clean_command()

    def clean_command(self):
        """ Fixes weird parameters and tells user about it """

        if str(self.timeout) == '' or not str(self.timeout).isnumeric(): 
            self.timeout = 3
            print("Added default timeout of 0 to command ", self.cmdid)

        if str(self.epoch) == '' or not str(self.epoch).isnumeric(): 
            self.epoch = 0
            print("Added default epoch of 0 to command ", self.cmdid)
        
        if str(self.cmd) == '': 
            self.cmd = 'ack'
            print("Added default command of 'ack' to command ", self.cmdid)

    def cmd_dict(self):
        """ returns dictionary representation required for Kivy, all values as string"""
        return self.__dict__
        # return {key: str(val) for key, val in self.__dict__.items()} # this was required when dict items had to be string
