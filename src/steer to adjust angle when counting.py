#!/usr/bin/env python3

from ev3dev2.button import Button
from ev3dev2.motor import MoveSteering, MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import ColorSensor, TouchSensor, UltrasonicSensor
from ev3dev2.sound import Sound
import math
import time

from ev3dev2 import *



class Robot:
    def __init__(self):
        self.tank_pair = MoveTank(OUTPUT_B, OUTPUT_C)
        self.steer_pair = MoveSteering(OUTPUT_B, OUTPUT_C)
        self.touch_sensor = TouchSensor()
        self.color = ColorSensor()
        self.ultrasonic = UltrasonicSensor()
        self.sound = Sound()
        self.btn = Button()
        self.tile_length = 199
        self.sensor_dist = 86
        # reflected light intensity of tiles
        self.black_range = range(0, 30)
        self.white_range = range(30, 100)

    def steer_on(steering, speed=20):
        self.steer_pair.on(steering=steering, speed=speed)

    def move_degrees(self, degrees, speed=20):
        if degrees > 0:
            self.tank_pair.on_for_degrees(left_speed=speed, right_speed=speed, degrees=degrees)
        else:
            self.tank_pair.on_for_degrees(left_speed=-speed, right_speed=-speed, degrees=-degrees)

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

    def turn(self, degrees):
        if (degrees == 0):
            return
        elif degrees > 0:
            self.tank_pair.on_for_degrees(left_speed=10, right_speed=-10, degrees=degrees*1.987)
        else:
            self.tank_pair.on_for_degrees(left_speed=-10, right_speed=10, degrees=-degrees*1.987)

    def run(self):
        self.initialize_start()
        self.count_tiles()
        self.initialize_tower()

    def initialize_start(self):
        self.move_degrees(90)
        self.skip_white()
        self.skip_black()
        self.skip_white()
        self.move_degrees(self.tile_length / 2 + sensor_dist)
        self.turn(degrees=90)
        self.skip_black(speed=-20)
        self.skip_white()

    def count_tiles(self):
        # skip first black tile, measure time taken
        tile_count = 1
        self.sound.play_tone(100 + (50 * tile_count), 0.5)
        start_time = time.time()
        self.skip_black()
        tile_time = time.time() - start_time()

        # skip over next 14 tiles
        while tile_count < 15:
            self.skip_white()
            tile_count += 1
            self.sound.play_tone(100 + (50 * tile_count), 0.5)

            # measure steering time to left side
            start_time = time.time()
            self.steer_on(steering=-50)
            while self.on_black():
                pass
            self.off()
            left_steer_time = time.time() - start_time
            start_time = time.time()
            self.steer_on(steering=-50, speed=-20)
            while time.time() - start_time < left_steer_time:
                pass
            self.off()

            # measure steering time to right side
            start_time = time.time()
            self.steer_on(steering=50)
            while self.on_black():
                pass
            self.off()
            right_steer_time = time.time() - start_time
            start_time = time.time()
            self.steer_on(steering=50, speed=-20)
            while time.time() - start_time < right_steer_time:
                pass
            self.off()

            # determine how much to turn
            difference_factor = (left_steer_time - right_steer_time) / tile_time
            if difference_factor >= 0:
                self.turn(degrees=-5)
            else:
                self.turn(degrees=5)

        self.move_degrees(-(self.tile_length*1.5 - self.sensor_dist))

    # point robot towards tower; return distance to tower
    def search_for_tower(self):
        min_dist = 255
        turn_thread = Thread(target=self.turn, args=[360])
        start_time = time.time()
        min_time = start_time
        turn_thread.start()
        
        while turn_thread.is_alive():
            cur_dist = self.ultrasonic.distance_centimeters
            if cur_dist < min_dist:
                min_dist = cur_dist
                min_time = time.time()

        end_time = time.time()
        turn_amount = 360*(min_time-start_time)/(end_time-start_time)
        if turn_amount <= 180:
            self.turn(degrees=turn_amount)
        else:
            self.turn(degrees=turn_amount-360)
        return min_dist

    def initialize_tower(self):
        self.turn(degrees=90)
        self.move_degrees(self.tile_length * 18, speed=50)
        
        while True:
            distance = self.search_for_tower()
            if distance / 2 <= 20:
                self.move_degrees(self.cm_to_degrees(distance-20))
                self.search_for_tower()
                break
            self.move_degrees(self.cm_to_degrees(distance/2))

        self.on(speed=100)
        start_time = time.time()
        while time.time() - start_time < 5:
            pass
        self.off()
        self.sound.speak("Mission complete")

    def cm_to_degrees(self, cm):
        return cm * 360 / (6 * math.pi)
    


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
