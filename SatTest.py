import time
import os
import queue
from houston_utils import *

# SatTest class
# this manages all of the data and keeps it available/synced in all view classes (Kivy tabs)

""" Other classes in the application can be notified of changes within this class,
    such as when we process a piece of telemetry and validate a command - which moves it
    from pending to acknowledged. 

    To notify other classes:
        - after creating an instance of the dependnat class, call sattest.attach_dependant(<object>)
        - your dependant class must implement update_from_sattest()
        - when data changes within sattest, sattest will call update_from_sattest() for all dependants
        - it will pass a reference to itself in through update_from_sattest()
        - your dependant classses can now poke at sattest attributes and use them
        - see RESPTab.py for an example
""" 

class SatTest():
    def __init__(self, tx_queue):
        self.new = [] # commands that have not yet been sent out to the OBC
        self.pending = [] # commands waiting on valid response or timeout
        self.acknowledged = [] # commands that have been acknowledged properly
        self.errored = [] # commands that timed out
        self.tx_queue = tx_queue # handle for the serial transmit queue
        self.epoch = time.time
        self.raw_data = [] # raw stuff coming in from the sat
        self.zero_epoch()
        self.dependants = [] # objects that will be notified of changes to sattest lists

    def check_response(self, telem, rx_time):
        # print ("SatTest rx: ", self.sat_epoch_at_unix(rx_time))
        # in the pending list, see if any expected responses match the telemetry
        # if yes, put the one with the lowest epoch + timeout

        # print("Telem to match: ", telem)
        telem = telem.strip()
        # print("Pending: ", self.pending[0].expect, telem)
        matches = [cmd for cmd in self.pending[:] if str(cmd.expect) == telem]  # list of all elements with .n==30
        # print("MATCH: ", [match.cmdid for match in matches]) 
        
        if len(matches) > 0:
            # sort matches and stuff
            for match in matches:
                print('Command #', match.cmdid, match.cmd, 'acknowledged at :', self.sat_epoch_at_unix(rx_time))
                #refactor
                self.add_to_acknowledged(match.cmdid)

            self.update_dependants('command_ack')        
     # when this runs, need to notify resptab to update

    def attach_dependant(self, dependant):
         # once we create the test, there are things that depend on its data, such as the response tab
         # dependants will all have a update_from_sattest method
         self.dependants.append(dependant)

    def update_dependants(self, method):
        """ Calls update_from_sattest method of all dependant objects so that they can update their data"""
        for dep in self.dependants:
            dep.update_from_sattest(self, method)

    def zero_epoch(self):
        self.unix_at_0 = time.time()

    def sat_epoch(self):
        return time.time() - self.unix_at_0

    def sat_epoch_at_unix(self, unix):
        return unix - self.unix_at_0 

    def add_schedule(self, data_in):
        # add a list of command objects
        print('Added ', len(data_in), 'commands to test schedule')
        self.add_to_new(data_in)
        self.update_dependants('add_schedule')

    def uplink(self, cmdid, dt):
        # print("CMDID_in", str(cmdid))
        self.add_to_pending(cmdid)
        command = self.pending[index_of_cmdid(self.pending, cmdid)]
        # print("Command: ", command.cmd_dict(), str(i))
        print("SCHEDULED COMMAND SEND: " + command.cmd)
        self.tx_queue.append(command.cmd)
        self.update_dependants('uplink')

        return

    def process_telem(self, telem):
        receive_time = self.sat_epoch()

        # telemetry comes back as several things:
        #   - orphan messages from testing
        #   - standard telem sets
        #   - responses to immediate commands
        #   - responses to scheduled commands are stored and can be requested, since we won't always be in contact 


        # Standard telem:
        # - parse telem packet and update views. This is things like epoch, battery state, etc.
        # - every time we get one, update the HUD. Have each set available as an expandable row in a list for examination
        # - if standard telem said there were errors in the queue, we would issue a command to retrieve them 
        # - for real mission: if there were errors, automatically request them 

        # Responses to command:
        # - search pending list for any commands with timeout >= receive time
        # - sort that by ID 
        # - search that list of commands for expected response matching this one
        # - if multiple matches, go with lowest ID. put the matched command on the acknowledged list

        # Command handling on sat: 
        # - if it's an immediate command, send out the response on radio/uart right away (this is for mission and testing)
        # - if it's a sat-scheduled command, log the response so we can pull it down later 
        # - if you want to do something like read a file, you could schedule a read command of that file at the time of next downlink

        # Ottawa test:
        # put in/out of different modes, observe that the telem is reflecting that
        #       - ex: safe mode, a bunch of tasks should be suspended. we can check that from a get tasks command
        #       - ex: low power mode, check that current has dropped
        #       - these things could be different modules that we load up to create a full test, then we run the whole thing
        # schedule commands for the future (such as a chime pass), verify that they execute
        # check that telem is nominal


    def command_timeout(self, cmdid, dt): # anything called by Clock should have dt argument
        """ Called by Kivy at timeout of command. 
        - if command is still on pending, it hasn't received a good response, so time it out
        """

        print('Checking timeout of command ID: ', cmdid)
        i = index_of_cmdid(self.pending[:], cmdid)
        if i != -1: # command is in pending and therefore timed out
            self.add_to_errored(i)
            self.update_dependants('errored')
            print("Command ID ", cmdid, " placed in errored.")

        return
        # pass
        # this will be called at the timeout time for a command by kivy clock
        # search the pending list for the command ID
        #   - if not there, no worries we've processed the command before timeout
        #   - if there, pull off and add to failed command list

    def add_to_new(self, data_in):
        """ add to new command list, update the state field """
        for command in data_in: command.state = 'new'
        self.new = data_in
        

    def add_to_pending(self, cmdid):
        """ add to pending, remove from new, update state field """
        i = index_of_cmdid(self.new, cmdid)
        command = self.new[i]
        command.state = 'pending'
        del self.new[i]
        self.pending.append(command)

    def add_to_acknowledged(self, cmdid):
        """ remove from pending, add to acknowledged, update state field """
        i = index_of_cmdid(self.pending, cmdid)
        command = self.pending[i]
        command.state = 'ack'
        self.acknowledged.append(command)
        del self.pending[i]

    def add_to_errored(self, i):
        """ remove from pending, add to errored, update state field """
        cmd = self.pending[i]
        cmd.state = 'errored'
        self.errored.append(cmd)
        del self.pending[i]