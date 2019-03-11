#!/usr/bin/env python3
from ev3dev2.button import Button
from ev3dev2.motor import MoveSteering, MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import ColorSensor, TouchSensor
from ev3dev2.sound import Sound
from threading import Thread


class Robot:
    def __init__(self):
        self.steer = MoveSteering(OUTPUT_B, OUTPUT_C)
        self.tank_pair = MoveTank(OUTPUT_B, OUTPUT_C)
        self.touch_sensor = TouchSensor()
        self.cl = ColorSensor()
        self.s = Sound()
        self.btn = Button()
        self.c_switch = True  # True: Turning left, comp right, False: opposite.
        self.col_switch = True  # True: black, False: white.
        self.tile_count = 0
        self.tile_length = 230
        # Sets up offset for variable light
        self.off_set = self.cl.reflected_light_intensity - 13
        self.black_range = range(0, 20)
        self.gray_range = range(self.black_range[len(self.black_range)-1], 50)
        self.white_range = range(self.gray_range[len(self.gray_range)-1], 100)

    def move_degrees(self, degrees):
        self.tank_pair.on_for_degrees(left_speed=20, right_speed=20, degrees=degrees)

    def run(self):
        # Moves the robot off starting pad and onto black-white tiles
        self.tank_pair.on_for_degrees(left_speed=50, right_speed=50, degrees=90)
        while (self.cl.reflected_light_intensity in self.black_range):
            self.tank_pair.on(left_speed=20, right_speed=20)
        self.tank_pair.off()
        while not (self.cl.reflected_light_intensity in self.black_range):
            self.tank_pair.on(left_speed=20, right_speed=20)
        self.tank_pair.off()
        self.tank_pair.on_for_degrees(left_speed=50, right_speed=50, degrees=self.tile_length*0.75)
        self.tank_pair.on_for_degrees(left_speed=20, right_speed=-20, degrees=180)
        while not (self.cl.reflected_light_intensity in self.white_range):
            self.tank_pair.on(left_speed=-20, right_speed=-20)
        self.tank_pair.off()
        self.tank_pair.on_for_degrees(left_speed=20, right_speed=20, degrees=self.tile_length*0.25)
        current_tile = self.getColour()
        self.center_robot(current_tile)
        while not (self.cl.reflected_light_intensity in current_tile):
            self.tank_pair.on(left_speed=20, right_speed=20)
        self.tank_pair.off()
        #self.tank_pair.on(left_speed=20, right_speed=20)
        t = Thread(target=self.move_degrees, args=(1.5 * self.tile_length))
        while (self.tile_count < 15):
            black_found = False
            print("starting")
            t.start()
            print("started")
            while t.is_alive():
                if (self.cl.reflected_light_intensity in self.black_range):
                    black_found = True
                    print("found black")
                    break

            self.tank_pair.off()
            if (black_found):
                self.tile_count +=1
                self.tank_pair.on(left_speed=20, right_speed=20)
                while not (self.cl.reflected_light_intensity in self.white_range):
                    pass
                self.tank_pair.off()
            else:
                self.realign()
        '''
        previous_tile_count = 0
        saw_black_realign = False
        saw_black = True
        while (self.tile_count < 15):
            if not (t.is_alive()):
                # check for realignment
                if (previous_tile_count < self.tile_count):
                    self.s.speak(str(self.tile_count))
                    previous_tile_count = self.tile_count
                if not (saw_black_realign):
                    self.realign()
                t.start()
                saw_black_realign = False
            if (self.cl.reflected_light_intensity in self.white_range and saw_black):
                self.tile_count +=1
                saw_black = False
                #self.tank_pair.off()
                #self.s.speak(str(self.tile_count))
                #self.tank_pair.on(left_speed=20, right_speed=20)
            if (self.cl.reflected_light_intensity in self.black_range):
                saw_black = True
                saw_black_realign = True
        self.tank_pair.off()
        '''
        '''
            if (self.cl.reflected_light_intensity > 55 and self.col_switch):
                self.tank_pair.off()
                self.titleCount += 1
                self.col_switch = False
                self.s.speak(str(self.titleCount))
                self.tank_pair.on(left_speed=20, right_speed=20)
            if (self.cl.reflected_light_intensity < 20 and not self.col_switch):
                self.col_switch = True
                '''

    def realign(self):
        # check side black is on
        self.s.speak("life is pain")

    # returns oposite colour
    def getColour(self):
        if (self.cl.reflected_light_intensity in self.black_range):
            return self.white_range
        elif (self.cl.reflected_light_intensity in self.white_range):
            return self.black_range
        else:
            self.s.speak("help me")
            return self.gray_range

    def center_robot(self, colour):
        right_turn_count = 0
        left_turn_count = 0
        #bias = 1/2
        while not (self.cl.reflected_light_intensity in colour or self.cl.reflected_light_intensity in self.gray_range):
            self.tank_pair.on_for_degrees(left_speed=10, right_speed=-10, degrees=10)
            right_turn_count +=1
        #if (self.cl.reflected_light_intensity in self.gray_range):
        #    bias = 3/4
        self.tank_pair.on_for_degrees(left_speed=-10, right_speed=10, degrees=10*right_turn_count)
        while not (self.cl.reflected_light_intensity in colour or self.cl.reflected_light_intensity in self.gray_range):
            self.tank_pair.on_for_degrees(left_speed=-10, right_speed=10, degrees=10)
            left_turn_count +=1
        #if (self.cl.reflected_light_intensity in self.gray_range):
        #    bias = 1/4
        #if (abs(left_turn_count-right_turn_count) < 2):
        #    bias = 1/2
        self.tank_pair.on_for_degrees(left_speed=10, right_speed=-10, degrees=(10*(right_turn_count+left_turn_count)/2))
        self.ninety_turn = 10*(right_turn_count+left_turn_count)/2

    def length_of_tile(self):
        count = 0
        while (self.cl.reflected_light_intensity in self.black_range):
            self.tank_pair.on_for_degrees(left_speed=10, right_speed=10, degrees=10)
            count +=1
        self.s.speak(str(count*10))



    def checkColour(self):
        while not self.btn.any():
            self.touch_sensor.wait_for_pressed()
            self.s.speak(str(self.cl.reflected_light_intensity))


if __name__ == "__main__":
    r = Robot()
    r.run()
