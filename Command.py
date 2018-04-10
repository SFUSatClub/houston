""" Command class
- maintains an internal represenation of the command as a dict, since that's required for Kivy Recycleviews
- using a class makes it easier for us to add command data fields ish ... 
- we also do validation of the inputs automatically
"""

class Command():
    def __init__(self, cmdid, cmd, epoch, timeout, expect, rel):
        self.dict_rep = {'cmdid': str(cmdid), 'cmd': str(cmd), 'epoch': str(epoch), 'timeout': str(timeout), 'expect': str(expect), 'rel': str(rel)}
        self.clean_command()
        self.update_internal()

    def clean_command(self):
        """ Fixes weird parameters and tells user about it """
        if self.dict_rep['timeout'] == '': 
            self.dict_rep['timeout'] = str(0)
            self.timeout = 0
            print("Added default timeout of 0 to command" + self.dict_rep['cmdid'])

        if self.dict_rep['epoch'] == '': 
            self.dict_rep['epoch'] = str(0)
            self.epoch = 0
            print("Added default epoch of 0 to command " + self.dict_rep['cmdid'])
        
        if self.dict_rep['cmd'] == '': 
            self.dict_rep['cmd'] = 'ack'
            self.cmd = 'ack'
            print("Added default command of 'ack' to command " + self.dict_rep['cmdid'])


    def cmd_dict(self):
        """ returns dictionary representation required for Kivy"""
        return self.dict_rep

    def cmd_dict_update(self, key, val):
        """ Allows entries to be edited, and checks them """
        self.dict_rep[key] = val
        self.clean_command()
        return self.dict_rep

    def update_internal(self): 
        """ Call after clean_command or else can get errors"""
        self.id = int(self.dict_rep['cmdid'])
        self.cmd = self.dict_rep['cmd']
        self.epoch = int(self.dict_rep['epoch'])
        self.timeout = int(self.dict_rep['timeout'])
        self.expect = self.dict_rep['expect']
        self.rel = self.dict_rep['rel']