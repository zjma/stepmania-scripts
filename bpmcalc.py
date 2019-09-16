#Prerequisite: python 3.7, pygame
import time
import pygame
M=8
def main():
    pygame.init()
    pygame.joystick.init()
    print(f'JoystickCount={pygame.joystick.get_count()}')
    joystick = pygame.joystick.Joystick(0) #The first joystick
    joystick.init()
    print(f'JoystickName={joystick.get_name()}')
    timestamps = []
    while True:
        e = pygame.event.wait()
        if e.type==10:
            timestamps.append(time.time())
            if len(timestamps)>=M+1:
                gapm=timestamps[-1]-timestamps[-M-1]
                print('BPM={:0>4.4f}'.format(60.0*M/gapm))

if __name__=='__main__': main()
