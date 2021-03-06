#!/usr/bin/python
# Paolo Arguelles (pa394) / Mike DiDomenico (md848)
# 3/7/19 - blink.py 
# ref:
# https://sourceforge.net/p/raspberry-gpio-python/wiki/PWM/ and 5725 lab 3

import RPi.GPIO as GPIO
import time
import numpy as np
import pygame
import os

# LEFT CCW BUTTON
def GPIO27_callback(channel):
    print "falling edge detected on 27"
    drive_servo(1, 1)

# LEFT CW BUTTON
def GPIO23_callback(channel):
    print "falling edge detected on 23"
    drive_servo(1, 2) 
    
# LEFT STOP BUTTON
def GPIO19_callback(channel):
    print "falling edge detected on 19"
    drive_servo(1, 3)
    
# RIGHT CCW BUTTON
def GPIO22_callback(channel):
    print "falling edge detected on 22"
    drive_servo(2, 1)

# RIGHT CW BUTTON
def GPIO17_callback(channel):
    print "falling edge detected on 17"
    drive_servo(2, 2)

# RIGHT STOP BUTTON    
def GPIO26_callback(channel):
    print "falling edge detected on 26"
    drive_servo(2, 3)
    
def initialize():

    # set up logs
    global start_time, left_log, right_log
    start_time = time.time()
    left_log = [('Stop', 0)] * 3
    right_log = [('Stop', 0)] * 3

    # set up GPIO mode
    GPIO.setmode(GPIO.BCM)
    # define servo pins
    global left_pin, right_pin
    left_pin = 12
    right_pin = 13
    GPIO.setup(left_pin, GPIO.OUT)
    GPIO.setup(right_pin, GPIO.OUT)

    # create global PWM objects and start
    global left_pwm, right_pwm
    left_pwm = GPIO.PWM(left_pin, 1)
    left_pwm.start(0)
    right_pwm = GPIO.PWM(right_pin, 1)
    right_pwm.start(0)
    
    # define GPIO ports
    ports = [17, 22, 23, 27, 19, 26]
    pull_up_ports = [17,22,23,27]
    for port in ports:
        if port in pull_up_ports:
            GPIO.setup(port, GPIO.IN,pull_up_down=GPIO.PUD_UP)
        else:
            GPIO.setup(port, GPIO.IN)
    # associate GPIO callbacks with pins
    GPIO.add_event_detect(17, GPIO.FALLING, callback=GPIO17_callback, bouncetime=300)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=GPIO22_callback, bouncetime=300)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=GPIO23_callback, bouncetime=300)
    GPIO.add_event_detect(19, GPIO.FALLING, callback=GPIO19_callback, bouncetime=300)
    GPIO.add_event_detect(26, GPIO.FALLING, callback=GPIO26_callback, bouncetime=300)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=GPIO27_callback, bouncetime=300)

    # setup pygame drivers and screen
    if True:
        os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
        os.putenv('SDL_FBDEV', '/dev/fb1') 
        os.putenv('SDL_MOUSEDRV', 'TSLIB') # Track mouse clicks on piTFT
        os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

def pygame_loop():
    # pygame and screen initialization
    pygame.init()
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    size = width, height = 320, 240
    black = 0, 0, 0
    screen = pygame.display.set_mode(size)

    # define left history text
    my_font = pygame.font.Font(None, 20)
    left_hist_text_surf = my_font.render('Left History', True, (255,255,255))
    left_hist_text_rect = left_hist_text_surf.get_rect(center=(width*3.0/16.0,height/4.0))
    # define right history text
    right_hist_text_surf = my_font.render('Right History', True, (255,255,255))
    right_hist_text_rect = right_hist_text_surf.get_rect(center=(width*13.0/16,height*1.0/4))
   
    # log info text objects
    my_font = pygame.font.Font(None, 20)
    #left
    left1 = my_font.render('stop 0', True, (255,255,255))
    left2 = my_font.render('stop 0', True, (255,255,255))
    left3 = my_font.render('stop 0', True, (255,255,255))
    
    right1 = my_font.render('stop 0', True, (255,255,255))
    right2 = my_font.render('stop 0', True, (255,255,255))
    right3 = my_font.render('stop 0', True, (255,255,255))
   
   # define quit button objects
    my_font = pygame.font.Font(None, 50)
    quit_surf = my_font.render('QUIT', True, (255,255,255))
    quit_rect = quit_surf.get_rect(right=width-5,bottom=height)
    
    # define panic button text
    my_font = pygame.font.Font(None, 30)
    panic_text_surf = my_font.render('STOP', True, (255,255,255))
    panic_text_rect = panic_text_surf.get_rect(center=(width/2,height/2))
    
    panic_radius = 55 
    panic_pressed = False

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            # mouse event
            if event.type is pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                # quit button pressed
                if quit_rect.collidepoint(pos):
                    print('on screen quit pressed')
                    done = True
                if ((pos[0]-width/2)**2+(pos[1]-height/2)**2)**(0.5) < panic_radius:
                    panic_pressed = not panic_pressed
                    if panic_pressed:
                        t = 'RESUME'
                        drive_servo(1,3)
                        drive_servo(2,3)
                    else:
                        t = 'STOP'
                        # RESUME left side    
                        if left_log[1][0] == 'CCW':
                            drive_servo(1,1)
                        elif left_log[1][0] == 'CW':
                            drive_servo(1,2)
                        else:
                            drive_servo(1,3)
                        # RESUME right side    
                        if right_log[1][0] == 'CCW':
                            drive_servo(2,1)
                        elif right_log[1][0] == 'CW':
                            drive_servo(2,2)
                        else:
                            drive_servo(2,3)

                    panic_text_surf = my_font.render(t, True, (255,255,255))
                    panic_text_rect = panic_text_surf.get_rect(center=(width/2,height/2))

        # update logs on screen
        my_font = pygame.font.Font(None, 20)
        left1 = my_font.render(str(left_log[0][0])+' '+str(left_log[0][1]), True, (255,255,255))
        left2 = my_font.render(str(left_log[1][0]) +' '+str(left_log[1][1]), True, (255,255,255))
        left3 = my_font.render(str(left_log[2][0]) +' '+str(left_log[2][1]), True, (255,255,255))
    
        right1 = my_font.render(str(right_log[0][0]) +' '+str(right_log[0][1]), True, (255,255,255))
        right2 = my_font.render(str(right_log[1][0]) +' '+str(right_log[1][1]), True, (255,255,255))
        right3 = my_font.render(str(right_log[2][0]) +' '+str(right_log[2][1]), True, (255,255,255))

        # render to display
        screen.fill(black)
        if panic_pressed:
            panic_color = (0,255,0)
        else:
            panic_color = (255,0,0)
        #panic button
        pygame.draw.circle(screen,panic_color, (width/2,height/2), panic_radius)
        screen.blit(panic_text_surf, panic_text_rect)
        # history
        screen.blit(left_hist_text_surf, left_hist_text_rect)
        screen.blit(right_hist_text_surf, right_hist_text_rect)
        #logs
        screen.blit(left1, left1.get_rect(center=(width*3.0/16, height*2.0/4)))
        screen.blit(left2, left2.get_rect(center=(width*3.0/16, height*2.5/4)))
        screen.blit(left3, left3.get_rect(center=(width*3.0/16, height*3/4)))
        screen.blit(right1, right1.get_rect(center=(width*13.0/16, height*2.0/4)))
        screen.blit(right2, right2.get_rect(center=(width*13.0/16, height*2.5/4)))
        screen.blit(right3, right3.get_rect(center=(width*13.0/16, height*3/4)))
        
        # quit button
        screen.blit(quit_surf, quit_rect)
        pygame.display.flip()
        clock.tick(30)

def drive_servo(servo_num, servo_cmd):
    global left_pwm, right_pwm, left_log, right_log, start_time

    # FULL SPEED COUNTER-CLOCKWISE    
    if servo_cmd == 1:
        freq, dc = get_param(1.7e-3)
        cmd = 'CCW'
    # FULL SPEED CLOCKWISE    
    elif servo_cmd == 2:
        freq, dc = get_param(1.3e-3)
        cmd = 'CW'
    # STOP    
    else:
        freq, dc = get_param(0)
        cmd = 'Stop'

    t = int(time.time() - start_time)
    if servo_num == 1: # Check if left servo    
        left_pwm.ChangeFrequency(freq)
        left_pwm.ChangeDutyCycle(dc)
        left_log = [(cmd, t)] + left_log
    else:
        right_pwm.ChangeFrequency(freq)
        right_pwm.ChangeDutyCycle(dc)
        right_log = [(cmd, t)] + right_log


def get_param(high):
    low = 20e-3
    period = high+low
    freq = 1/(period)
    dc = high/(period)*100
    
    if freq == 0:
        freq = 1
    
    return freq, dc
    
    

def main():
    try:
        # Initialize servos
        initialize()
        
        # User input to stop
        pygame_loop() 
        
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()

