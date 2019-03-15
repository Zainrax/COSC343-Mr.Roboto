#!/usr/bin/env python3
from threading import Thread

from ev3dev2.button import Button
from ev3dev2.motor import MoveSteering, MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import ColorSensor, TouchSensor, UltrasonicSensor
from ev3dev2.sound import Sound
import math

from ev3dev2 import *



class Robot:
    def __init__(self):
        self.steer = MoveSteering(OUTPUT_B, OUTPUT_C)
        self.tank_pair = MoveTank(OUTPUT_B, OUTPUT_C)
        self.touch_sensor = TouchSensor()
        self.cl = ColorSensor()
        self.ultraSonic = UltrasonicSensor()
        self.s = Sound()
        self.btn = Button()
        self.c_switch = True  # True: Turning left, comp right, False: opposite.
        self.col_switch = True  # True: black, False: white.
        self.tile_count = 0
        self.tile_length = 199
        # Sets up offset for variable light
        self.off_set = self.cl.reflected_light_intensity - 13
        self.black_range = range(0, 30)
        self.gray_range = range(self.black_range[len(self.black_range) - 1], 50)
        self.white_range = range(self.gray_range[len(self.gray_range) - 1], 100)
        self.sensor_dist = 86

    def move_degrees(self, degrees, speed=20):
        if degrees > 0:
            self.tank_pair.on_for_degrees(left_speed=speed, right_speed=speed, degrees=degrees)
        else:
            self.tank_pair.on_for_degrees(left_speed=-speed, right_speed=-speed, degrees=-degrees)

    def on(self, speed=20):
        self.tank_pair.on(left_speed=speed, right_speed=speed)

    def off(self):
        self.tank_pair.off()

    def check_colour(self):
        while (self.tile_count < 15):
            if (self.cl.reflected_light_intensity in self.white_range and self.col_switch):
                self.titleCount += 1
                self.col_switch = False
                self.s.speak(str(self.titleCount))
            if (self.cl.reflected_light_intensity in self.black_range and not self.col_switch):
                self.col_switch = True

    def run(self):
        # Moves the robot off starting pad and onto black-white tiles
        self.initialize_start()
        self.count_tiles()
        self.initialise_tower()

    def on_white(self):
        return (self.cl.reflected_light_intensity in self.white_range)

    def on_black(self):
        return (self.cl.reflected_light_intensity in self.black_range)

    def turn(self, degrees):
        if (degrees == 0): return
        self.tank_pair.on_for_degrees(left_speed=10*(degrees/abs(degrees)), right_speed=-10*(degrees/abs(degrees)), degrees=abs(degrees)*1.987)

    def count_tiles(self):
        tile_count = 0
        self.on()
        while self.on_black():
            pass
        self.off()
        tile_count +=1
        self.s.play_tone(200 * tile_count, 0.5)
        while tile_count < 14:
            # skip over white tiles
            self.on()
            while self.on_white():
                pass
            self.off()

            # found a black tile; move to its centre
            self.move_degrees(degrees=self.tile_length*0.5 + self.sensor_dist)

            # find distance from centre of black tile to right-edge of black tile
            self.turn(degrees=90)
            right_dist = self.sensor_dist
            while self.on_black():  # find right_dist
                self.move_degrees(degrees=8)
                right_dist += 8

            # move robot back to centre
            self.move_degrees(degrees=-(right_dist - self.sensor_dist))

            # find distance from centre of black tile to left-edge of black tile
            self.turn(degrees=-180)
            left_dist = self.sensor_dist
            while self.on_black():  # find left_dist
                self.move_degrees(degrees=8)
                left_dist += 8

            # drive robot to centre
            middle_dist = (right_dist + left_dist) / 2
            self.move_degrees(degrees=self.sensor_dist)
            self.turn(degrees=180)
            self.move_degrees(degrees=middle_dist)

            # adjust robot's direction
            angle_correction = 0.6*math.degrees(math.acos(1 / math.sqrt(1 + (0.25 - 0.5 * left_dist / self.tile_length) ** 2)))
            if left_dist < self.tile_length / 2:
                self.turn(degrees=-90 + angle_correction)
            else:
                self.turn(-90 - angle_correction)
            self.on()
            while self.on_black():
                pass
            self.off()
            tile_count +=1
            self.s.play_tone(200*tile_count, 0.5)
        self.on()
        while self.on_white():
            pass
        self.off()
        tile_count +=1
        self.s.play_tone(100 + (50 * tile_count), 0.5)
        self.move_degrees(self.tile_length + self.sensor_dist)

    def initialize_start(self):
        self.move_degrees(90)
        while self.on_black():
            self.on()
        self.off()
        while self.on_white():
            self.on()
        self.off()
        self.move_degrees(self.tile_length * 0.75)
        self.move_degrees(180)
        while self.on_black():
            self.on()
        self.off()
        self.move_degrees(self.tile_length * 0.25)
        current_tile = self.get_opposite_colour()
        self.center_robot(current_tile)
        while not (self.cl.reflected_light_intensity in current_tile):
            self.on()
        self.off()

    def realign(self):
        self

    def get_opposite_colour(self):
        if self.on_black():
            return self.white_range
        else:
            return self.black_range

    def center_robot(self, colour):
        right_turn_count = 0
        left_turn_count = 0
        while not (self.cl.reflected_light_intensity in colour):
            self.turn(degrees=5)
            right_turn_count += 1
        self.turn(degrees=-5*right_turn_count)
        while not (self.cl.reflected_light_intensity in colour):
            self.turn(degrees=-5)
            left_turn_count += 1
        self.turn(degrees=2.5*(right_turn_count + left_turn_count))

    def degrees_to_cm(self, degrees):
        return 360/(11*math.pi)

    def search_for_tower(self):
        turn_count = 0
        while (self.ultraSonic.distance_centimeters > 100):
            self.turn(5)
            turn_count += 5
            # move a short distance to get a better position then search again
            if turn_count >= 360:
                self.move_degrees(self.tile_length)
                turn_count = 0
        turn_count = 0
        while (self.ultraSonic.distance_centimeters < 100):
            self.turn(5)
            turn_count += 5
        self.turn(-turn_count/2)

    # This points robot towards the tower then returns its distance in cm.
    def initialise_tower(self):
        self.turn(degrees=90)
        self.move_degrees(self.tile_length * 18, speed=100)
        while not self.touch_sensor.is_pressed:
            if self.ultraSonic.distance_centimeters < 100:
                self.move_degrees(self.tile_length/2)
            else:
                self.search_for_tower()
        #self.s.speak("exited search routine")
        self.on(speed=100)
        while self.on_black():
            pass
        self.off()
        self.s.speak("Mission Completed")


if __name__ == "__main__":
    r = Robot()
    try:
        r.run()
    except:
        import traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
        while True:
            pass
