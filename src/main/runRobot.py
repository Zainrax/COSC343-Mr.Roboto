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
        # Ranges for color intensities
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
        return self.color_sensor.reflected_light_intensity in self.white_range

    def on_black(self):
        return self.color_sensor.reflected_light_intensity in self.black_range

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
        self.move_degrees(80)
        self.skip_black()
        self.skip_white()
        self.move_degrees(self.tile_length / 2 + self.sensor_dist)
        self.turn(degrees=90)
        self.skip_white(speed=-20)
        self.skip_black(speed=-20)
        self.skip_white()

    def get_angle_from_color(self, left2, left1, right1, right2):
        num = 0
        if not left2:
            num += 8
        if not left1:
            num += 4
        if not right1:
            num += 2
        if not right2:
            num += 1

        angle_list = [0, -7, 3.5, 7, -3.5, -7, 0, 3.5, 7, 0, 7, 7, -7, -7, -3.5, 0]
        return angle_list[num]

    def count_tiles(self):
        tile_count = 0
        turn_angle = 0
        prev_turn_angle = 0

        while tile_count < 14:
            tile_count += 1
            self.sound.play_tone(100 + (50 * tile_count), 0.5)
            self.move_degrees(135)
            
            self.turn(90)
            right_is_white_1 = self.on_white()
            self.move_degrees(40)
            right_is_white_2 = self.on_white()
            self.move_degrees(-40)
            self.turn(-180)
            left_is_white_1 = self.on_white()
            self.move_degrees(40)
            left_is_white_2 = self.on_white()
            self.move_degrees(-40)
            self.turn(90)

            turn_angle = self.get_angle_from_color(left_is_white_2, left_is_white_1, right_is_white_1, right_is_white_2)
            if prev_turn_angle > 0 and turn_angle > 0:
                turn_angle = 3.5
            elif prev_turn_angle < 0 and turn_angle < 0:
                turn_angle = -3.5
            elif turn_angle == 0:
                self.turn(-prev_turn_angle)
            self.turn(turn_angle)
            prev_turn_angle = turn_angle
            
            self.skip_black()
            self.skip_white()

        tile_count += 1
        self.sound.play_tone(100 + (50 * tile_count), 0.5)
        self.move_degrees(self.tile_length)

    def cm_to_degrees(self, cm):
        return (360/(6*math.pi))*cm

    def turn_360(self):
        self.turn(degrees=370)

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
        self.turn(degrees=-370)
        self.turn(degrees=370*(min_time-start_time)/(end_time-start_time))
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

        self.move_degrees(self.cm_to_degrees(10), speed=20)
        for i in range(40,101,10):
            self.move_degrees(self.tile_length*2, speed=i)
            self.move_degrees(-self.tile_length, speed=50)
        for i in range(5):
            self.move_degrees(self.tile_length*2, speed=100)
            self.move_degrees(-self.tile_length, speed=50)
        self.on(speed=100)
        time.sleep(5)
        self.off()
        self.sound.play_tone(400, 1)


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
