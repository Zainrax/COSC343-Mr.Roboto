#!/usr/bin/env python3
import math
import time
from threading import Thread

from ev3dev2 import *
from ev3dev2.button import Button
from ev3dev2.motor import MoveSteering, MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor import INPUT_1, INPUT_2
from ev3dev2.sensor.lego import ColorSensor, TouchSensor, UltrasonicSensor
from ev3dev2.sound import Sound


class Robot:
    def __init__(self):
        self.steer_pair = MoveSteering(OUTPUT_B, OUTPUT_C)
        self.tank_pair = MoveTank(OUTPUT_B, OUTPUT_C)
        self.touch_sensor_left = TouchSensor(INPUT_1)
        self.touch_sensor_right = TouchSensor(INPUT_2)
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

    def steer_on(self, steering, speed=20):
        if (steering > 0):
            self.tank_pair.on(left_speed=speed, right_speed=0)
        elif (steering < 0):
            self.tank_pair.on(left_speed=0, right_speed=speed)

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

    def skip_white(self, speed=20):
        self.on(speed=speed)
        while self.on_white():
            pass
        self.off()

    def skip_black(self, speed=20):
        self.on(speed=speed)
        while self.on_black():
            pass
        print("skipping black")
        self.off()

    def turn(self, degrees, speed=20):
        if degrees >= 0:
            self.tank_pair.on_for_degrees(left_speed=speed, right_speed=-speed, degrees=degrees * 1.987)
        else:
            self.tank_pair.on_for_degrees(left_speed=-speed, right_speed=speed, degrees=-degrees * 1.987)

    def count_tiles(self):
        # skip first black tile, measure time taken
        tile_count = 1

        while tile_count < 15:
            self.s.play_tone(100 + (50 * tile_count), 0.5)
            self.move_degrees(self.tile_length / 2)
            self.turn(90, speed=40)
            self.move_degrees(40)
            right_is_white = self.on_white()
            self.move_degrees(-40)
            self.turn(180, speed=40)
            self.move_degrees(40)
            left_is_white = self.on_white()
            self.move_degrees(-40)
            self.turn(-270, speed=40)

            if left_is_white and not (right_is_white):
                self.turn(12)
            elif not (left_is_white) and right_is_white:
                self.turn(-12)

            self.skip_black()
            self.skip_white()
            tile_count += 1
        self.s.play_tone(50, 0.5)
        self.move_degrees(-self.tile_length * 0.5)


    def initialize_start(self):
        self.move_degrees(90)
        self.skip_white()
        self.skip_black()
        self.skip_white()
        self.move_degrees(self.tile_length / 2 + self.sensor_dist)
        self.turn(degrees=90)
        self.skip_black(speed=-20)
        self.skip_white()

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

    def cm_to_degrees(self, cm):
        return (360/(6*math.pi))*cm

    def turn_360(self):
        self.turn(degrees=360)

    def search_for_tower(self):
        min_dist = 255
        start_time = time.time()
        min_time = start_time
        turn_thread = Thread(target=self.turn_360)
        turn_thread.start()
        while turn_thread.is_alive():
            cur_dist = self.ultraSonic.distance_centimeters
            if cur_dist < min_dist:
                min_dist = cur_dist
                min_time = time.time()
        end_time = time.time()
        self.turn(degrees=360*(min_time-start_time)/(end_time-start_time))
        # self.s.speak(str(min_dist))
        return min_dist


        # turn_count = 0
        # min = 255
        # turn_to_min = 0
        # while (turn_count < 360):
        #     if (self.touch_sensor_left.is_pressed or self.touch_sensor_right.is_pressed):
        #         return
        #     self.turn(5)
        #     if self.ultraSonic.distance_centimeters < min:
        #         min = self.ultraSonic.distance_centimeters
        #         turn_to_min = turn_count
        #     turn_count += 5
        # self.turn(turn_to_min)
        # return min

    # This points robot towards the tower then returns its distance in cm.
    def initialise_tower(self):
        self.turn(degrees=90)
        self.move_degrees(self.tile_length * 18, speed=80)
        just_found_tower = False
        while not (self.touch_sensor_left.is_pressed or self.touch_sensor_right.is_pressed):
            distance = self.search_for_tower()
            if distance/2 <= 20:
                self.move_degrees(self.cm_to_degrees(distance-20))
                self.search_for_tower()
                break
            self.move_degrees(self.cm_to_degrees(distance/2))
        self.on(speed=100)
        while not (self.touch_sensor_right.is_pressed or self.touch_sensor_left.is_pressed):
            pass
        while self.on_white():
            pass
        self.off()
        self.move_degrees(self.tile_length*2, speed=100)
        self.on(speed=100)
        while self.on_black():
            pass
        self.off()
        self.s.speak("Mission Completed")

    def get_distance(self):
        while True:
            print(self.ultraSonic.distance_centimeters)


if __name__ == "__main__":
    try:
        r = Robot()
        r.run()

    except:
        import traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
        while True:
            pass
