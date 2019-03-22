#!/usr/bin/env python3
import math
import time
from threading import Thread

from ev3dev2 import *
from ev3dev2.button import Button
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import ColorSensor, TouchSensor, UltrasonicSensor
from ev3dev2.sound import Sound


class Robot:
    def __init__(self):
        self.tank_pair = MoveTank(OUTPUT_B, OUTPUT_C)
        self.color_sensor = ColorSensor()
        self.ultrasonic = UltrasonicSensor()
        self.sound = Sound()
        self.tile_length = 200
        # Sets up offset for variable light
        self.black_range = range(0, 30)
        self.white_range = range(30, 100)
        self.sensor_dist = 86

    def move_degrees(self, degrees, speed=20):
        if degrees >= 0:
            self.tank_pair.on_for_degrees(left_speed=speed, right_speed=speed, degrees=degrees)
        else:
            self.tank_pair.on_for_degrees(left_speed=-speed, right_speed=-speed, degrees=-degrees)

    def steer_on(self, steering, speed=20):
        if steering >= 0:
            self.tank_pair.on(left_speed=speed, right_speed=0)
        else:
            self.tank_pair.on(left_speed=0, right_speed=speed)

    def on(self, speed=20):
        self.tank_pair.on(left_speed=speed, right_speed=speed)

    def off(self):
        self.tank_pair.off()

    def on_white(self):
        return self.color.reflected_light_intensity in self.white_range

    def on_black(self):
        return self.color.reflected_light_intensity in self.black_range

    def skip_white(self, speed=20):
        self.on(speed=speed)
        while self.on_white():
            pass
        self.off()

    def skip_black(self, speed=20):
        self.on(speed=speed)
        while self.on_black():
            pass
        self.off()

    def turn(self, degrees, speed=20):
        if degrees >= 0:
            self.tank_pair.on_for_degrees(left_speed=speed, right_speed=-speed, degrees=degrees * 1.987)
        else:
            self.tank_pair.on_for_degrees(left_speed=-speed, right_speed=speed, degrees=-degrees * 1.987)

    def run(self):
        self.initialize_start()
        self.count_tiles()
        self.bump_tower()

    def initialize_start(self):
        self.move_degrees(90)
        self.skip_white()
        self.skip_black()
        self.skip_white()
        self.move_degrees(self.tile_length / 2 + self.sensor_dist)
        self.turn(degrees=90)
        self.skip_black(speed=-20)
        self.skip_white()

    def count_tiles(self):
        tile_count = 0
        turn_angle = 0
        prev_turn_angle = 0

        while tile_count < 15:
            tile_count += 1
            self.sound.play_tone(100 + (50 * tile_count), 0.5)
            self.move_degrees(self.tile_length / 2)
            
            self.turn(90)
            self.move_degrees(40)
            right_is_white = self.on_white()
            self.move_degrees(-40)
            self.turn(-180)
            self.move_degrees(40)
            left_is_white = self.on_white()
            self.move_degrees(-40)
            self.turn(90)

            if left_is_white and not(right_is_white):
                turn_angle = 7
            elif not(left_is_white) and right_is_white:
                turn_angle = -7
            else:
                turn_angle = 0
                self.turn(-prev_turn_angle)
            self.turn(turn_angle)
            prev_turn_angle = turn_angle
            
            self.skip_black()
            self.skip_white()
            
        self.move_degrees(-self.tile_length * 0.5)

    def cm_to_degrees(self, cm):
        return (360/(6*math.pi))*cm

    def turn_360(self):
        self.turn(degrees=360)

    # point robot towards tower; return distance in cm
    def search_for_tower(self):
        min_dist = 255
        start_time = time.time()
        min_time = start_time
        turn_thread = Thread(target=self.turn_360)
        turn_thread.start()
        while turn_thread.is_alive():
            cur_dist = self.ultrasonic.distance_centimeters
            if cur_dist < min_dist:
                min_dist = cur_dist
                min_time = time.time()
        end_time = time.time()
        self.turn(degrees=-360)
        self.turn(degrees=360*(min_time-start_time)/(end_time-start_time))
        return min_dist

    def bump_tower(self):
        self.turn(degrees=90)
        self.move_degrees(self.tile_length * 18)
        
        while True:
            distance = self.search_for_tower()
            if distance / 2 <= 20:
                self.move_degrees(self.cm_to_degrees(distance-20))
                self.search_for_tower()
                break
            self.move_degrees(self.cm_to_degrees(distance/2))
            
        self.on(speed=100)
        time.sleep(5)
        self.off()
        self.sound.speak("Mission Completed")


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
