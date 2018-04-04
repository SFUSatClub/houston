import serial
import time

#https://stackoverflow.com/questions/13180941/how-to-kill-a-while-loop-with-a-keystroke

serialPort = '/dev/cu.usbserial-A700eYE7'
#serialPort = '/dev/tty.usbserial-DM007SVA'
#serialPort = '/dev/cu.usbserial-DM007SVA'

log = open("data.txt", "a")
log.write("\r\n" + "Began test:" + str(time.time()) + "\r\n")


def read_serial():
    try:
        with serial.Serial(serialPort, 115200, timeout = 10) as ser:
            offset = time.time()

            while(1):
                line = ser.readline()

                if len(line) > 1: # this catches the weird glitch where I only get out one character
                    print time.time() - offset,':',line
                    log.write(str(time.time() - offset) + ',' + line)
                #
                # if line[-3] == '9':
                #     msg = ('s','t','a','t','e',' ','g','e','t','\r','\n','\0')
                #     for character in msg:
                #         ser.write(character)
                #         # time.sleep(0.01)


    except Exception as error:
        time.sleep(0.5)
        print 'Waiting for serial...'
        log.write('Waiting for serial: ' + str(time.time()) + '\r\n')
        read_serial()


try:
    while True:
        read_serial()
except KeyboardInterrupt:
    log.close()
    pass
