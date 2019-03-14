from math import sqrt, acos

# assumes we start on white

sensor_dist = 10 # degrees rotation between wheels and sensor
tile_length = 270
tile_count = 0

while tile_count < 15:
    #skip over white tiles
    motor.on()
    while on_white():
        pass
    motor.off()

    # found a black tile; move to its centre
    motor.on_for(degrees=tile_length/2+sensor_dist)

    # find distance from centre of black tile to right-edge of black tile
    self.turn(degrees=90)
    right_dist = sensor_dist
    while on_black(): # find right_dist
        motor.on_for(degrees=10)
        right_dist += 10

    #move robot back to centre
    motor.on_for(degrees=-(right_dist-sensor_dist))

    # find distance from centre of black tile to left-edge of black tile
    self.turn(degrees=-180)
    left_dist = sensor_dist
    while on_black(): # find left_dist
        motor.on_for(degrees=10)
        left_dist += 10

    #drive robot to centre
    middle_dist = (right_dist + left_dist) / 2
    motor.on_for(degrees=sensor_dist)
    self.turn(degrees=180)
    self.on_for(degrees=middle_dist)

    # adjust robot's direction
    angle_correction = math.degrees(math.acos( 1/math.sqrt(1+(0.25-0.5*left_dist/tile_length)**2) ))
    if left_dist < tile_length / 2:
        self.turn(degrees=-90+angle_correction)
        
