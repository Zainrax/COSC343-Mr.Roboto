#!/usr/bin/env python3
from ev3dev2.button import Button
from ev3dev2.motor import MoveSteering, MoveTank, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import ColorSensor, TouchSensor
from ev3dev2.sound import Sound


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
        self.titleCount = 1
        # Sets up offset for variable light
        self.off_set = self.cl.reflected_light_intensity - 13
        self.black_range = range(0, 20 + off_set)
        self.gray_range = range(self.black_range[len(self.black_range)-1], 55+off_set)
        self.white_range = range(self.gray_range[len(self.gray_range)-1], 100)

    def run(self):
        # Moves the robot off starting pad and onto black-white tiles
        self.tank_pair.on_for_rotations(left_speed=50, right_speed=50, rotations=0.5)
        self.tank_pair.on_for_degrees(left_speed=50, right_speed=0, degrees=400)
        self.tank_pair.on(left_speed=20, right_speed=20)
        if (self.cl.reflected_light_intensity in self.white_range):
            self.col_switch = False
        elif (self.cl.reflected_light_intensity < 20):
            self.col_switch = True
        else:
            self.s.speak("Help me")
        while not self.btn.any():
            if (self.cl.reflected_light_intensity > 30 and self.cl.reflected_light_intensity < 55):
                self.tank_pair.off()
                if (self.c_switch):
                    self.tank_pair.on_for_degrees(left_speed=50, right_speed=0, degrees=90)
                    self.c_switch = False
                else:
                    self.tank_pair.on_for_degrees(left_speed=0, right_speed=50, degrees=90)
                    self.c_switch = True

                self.tank_pair.on(left_speed=20, right_speed=20)
                while (True):
                    if (
                            self.cl.reflected_light_intensity < 20 or self.cl.reflected_light_intensity > 55 or self.btn.any()):
                        break

            if (self.cl.reflected_light_intensity > 55 and self.col_switch):
                self.tank_pair.off()
                self.titleCount += 1
                self.col_switch = False
                self.s.speak(str(self.titleCount))
                self.tank_pair.on(left_speed=20, right_speed=20)
            if (self.cl.reflected_light_intensity < 20 and not self.col_switch):
                self.col_switch = True

    def checkColour(self):
        while not self.btn.any():
            self.touch_sensor.wait_for_pressed()
            self.s.speak(str(self.cl.reflected_light_intensity))


if __name__ == "__main__":
    r = Robot()
    r.run()
