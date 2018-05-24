""" OBC Simulator 

- facilitates testing Houston without needing an OBC
- to send something to the OBC, call self.sim_transmit()


"""
import queue

class simulator():
    def __init__(self):
        self.tx_queue = queue.Queue()
        # TODO: make a self.state variable that's an enum of STATE_SAFE, STATE_READY, STATE_LOW_POWER. Start at safe. 

    def sim_rx(self, message):
        """ Simulator receive, the OBC calls this to send stuff to the simulator """
        if message.lower() == 'ack':
            self.sim_transmit('Ack!')

        # TODO: insert more if statements and send out fake responses 
        # TODO: state set and get command
        
    def sim_transmit(self, message):
        """ Add something to our queue so that Houston can receive it """
        self.tx_queue.put(message)

    def sim_tx(self):
        """ Mimics OBC sending things out to us.
            Called by Houston repeatedly. 
            If it's time to send something, return it as a string """

        # call any functions to simulate repeated satellite telemetry here
        self.send_std_telem()

        # if we have something to send out, send the first thing
        if self.tx_queue.qsize() > 0:
            return self.tx_queue.get()
        else: 
            return None

    def send_std_telem(self):
        pass

        # Todo: send out a set of standard telemetry once every few seconds
        # the telemetry can look like: '<time since construction in seconds>, <random letter a-d>, <random number 0-2>, <random number 0-100>' 
        # if it's been a few seconds since the last time we sent, call self.sim_transmit(the_fake_data). Otheriwse, do nothing