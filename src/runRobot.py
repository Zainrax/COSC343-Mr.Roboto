#!/usr/bin/env python3
from threading import Thread

from ev3dev2.button import Button
from ev3dev2.motor import MoveSteering, MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import ColorSensor, TouchSensor, UltrasonicSensor
from ev3dev2.sound import Sound


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
        self.tile_length = 230
        # Sets up offset for variable light
        self.off_set = self.cl.reflected_light_intensity - 13
        self.black_range = range(0, 30)
        self.gray_range = range(self.black_range[len(self.black_range) - 1], 50)
        self.white_range = range(self.gray_range[len(self.gray_range) - 1], 100)

    def move_degrees(self, degrees):
        self.tank_pair.on_for_degrees(left_speed=20, right_speed=20, degrees=degrees)

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
        colour_thread = Thread(target=self.check_colour)
        # Moves the robot off starting pad and onto black-white tiles
        self.initialize_start()
        colour_thread.start()
        while (colour_thread.is_alive()):
            self.move_degrees(180)



    def initialize_start(self):
        self.move_degrees(90)
        while (self.cl.reflected_light_intensity in self.black_range):
            self.on()
        self.off()
        while not (self.cl.reflected_light_intensity in self.black_range):
            self.on()
        self.off()
        self.move_degrees(self.tile_length * 0.75)
        self.move_degrees(180)
        while not (self.cl.reflected_light_intensity in self.white_range):
            self.on()
        self.off()
        self.move_degrees(self.tile_length * 0.25)
        current_tile = self.getColour()
        self.center_robot(current_tile)
        while not (self.cl.reflected_light_intensity in current_tile):
            self.on()
        self.off()

    def realign(self):
        self

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
        while not (self.cl.reflected_light_intensity in colour):
            self.tank_pair.on_for_degrees(left_speed=10, right_speed=-10, degrees=10)
            right_turn_count += 1
        self.tank_pair.on_for_degrees(left_speed=-10, right_speed=10, degrees=10 * right_turn_count)
        while not (self.cl.reflected_light_intensity in colour):
            self.tank_pair.on_for_degrees(left_speed=-10, right_speed=10, degrees=10)
            left_turn_count += 1
        self.tank_pair.on_for_degrees(left_speed=10, right_speed=-10,
                                      degrees=(10 * (right_turn_count + left_turn_count) / 2))

    # This points robot towards the tower then returns its distance in cm.
    def find_tower(self):
        while (self.ultraSonic.distance_centimeters > 100):
            self.tank_pair.on(left_speed=10, right_speed=-10)

        self.off()


if __name__ == "__main__":
    r = Robot()
    r.run()
