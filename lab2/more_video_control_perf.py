#
# jfs9 9/10/17  GPIO example python script
# md848/pa394 2/21/19 added support for sixth button
# md848/pa394 added more video control
#

import RPi.GPIO as GPIO
import time

startTime = time.time()

fifo_path = '/home/pi/labs/lab2/video_fifo'

GPIO.setmode(GPIO.BCM)   # Set for broadcom numbering not board numbers...
# setup piTFT buttons
# 17 22 23 27
ports = [17, 22, 23, 27, 19, 26]
pull_up_ports = [17,22,23,27]
#
quit_port = 27

#                        V need this so that button doesn't 'float'!
for port in ports:
        if port in pull_up_ports:
            GPIO.setup(port, GPIO.IN,pull_up_down=GPIO.PUD_UP)
        else:
            GPIO.setup(port, GPIO.IN)

while True:
    timeElapsed = time.time()-startTime
    #print 'elapsed time:' + str(timeElapsed)
    if timeElapsed >= 10:
        exit()

    #time.sleep(20e-6)  # Without sleep, no screen output!
    for port in ports:
        if ( not GPIO.input(port) ):
            print "Button "+ str(port) + " has been pressed...."
            inp = ''
            if port == 17:
                inp = 'pause\n'
            elif port == 22:
                inp = 'seek 10\n'
            elif port == 23:
                inp = 'seek -10\n'
            elif port == 26:
                inp = 'seek -30\n'
            elif port == 19:
                inp = 'seek 30\n'
            elif port == quit_port:
               inp = 'q\n'

            f = open(fifo_path, 'w')
            f.write(inp)
            f.close()

            if port == quit_port:
               exit()
            #time.sleep(0.3)

