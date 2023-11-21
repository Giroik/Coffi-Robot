#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

import time


class Map:
    """
        Constructor for the Map class.

        Parameters:
        - rows: Number of rows in the map.
        - columns: Number of columns in the map.
        - center: Center of the map.
        - userPositions: List of user positions, each represented by [row, column, value].
        - blockAria: Width of the blocked area on each side of the map.
        - finalStep: The final step to mark in the map.
    """

    def __init__(self, rows, columns, center, userPositions, blockAria, finalStep):
        self.rows = rows
        self.columns = columns
        self.center = center
        self.map = [[-1 for _ in range(columns)] for _ in range(rows)]
        self.userPositions = userPositions
        self.blockAria = blockAria
        self.finalStep = finalStep
        self.userInputsSetToSteps()

    """
        Converts user positions to steps by dividing the first element of each position by 20.
    """

    def userInputsSetToSteps(self):
        for i in range(len(self.userPositions)):
            self.userPositions[i][0] = self.userPositions[i][0] // 20

    """
        Draws a new map based on user positions, blocked areas, and the final step which was given in constructor.
    """

    def drawNewMap(self):
        for i in range(len(self.map) - 1):
            if (i < self.finalStep):
                self.map[i][17] = 0
        for row in self.map:
            for i in range(self.blockAria):
                row[i] = -2

        for row in self.map:
            for i in range(self.blockAria):
                row[columns - 1 - i] = -2

        for i in range(len(userPositions)):
            self.map[self.userPositions[i][0]][self.userPositions[i][1]] = self.userPositions[i][2]
            if (self.userPositions[i][1] > 17):
                a = 0
                while (self.map[self.userPositions[i][0]][18 + a] == -1):
                    self.map[self.userPositions[i][0]][18 + a] = self.userPositions[i][2]
                    a += 1

            elif (self.userPositions[i][1] < 17):
                a = 0
                while (self.map[self.userPositions[i][0]][16 - a] == -1):
                    self.map[self.userPositions[i][0]][16 - a] = self.userPositions[i][2]
                    a += 1

    """
        Prints all rows from the map array 
    """

    def printMap(self):
        for row in self.map:
            print(row)

    """
        This method return map with positions of users and high way 
    """

    def getMap(self):
        return self.map

    """
        This method return middle of the array list of map
    """

    def getCenter(self):
        return self.center


class Programm:
    """
        Constructor for the Programm class.

        Parameters:
        - map: An instance of the Map class representing the environment.
        - center: Center of the map.
    """

    def __init__(self, map):
        self.coffiRobot = EV3Brick()
        self.motorRight = Motor(Port.A, positive_direction=Direction.CLOCKWISE, gears=None)
        self.motorLeft = Motor(Port.B, positive_direction=Direction.CLOCKWISE, gears=None)
        self.motorElevator = Motor(Port.D, positive_direction=Direction.CLOCKWISE, gears=None)
        self.robotBotton = TouchSensor(Port.S3)
        self.wheels = DriveBase(self.motorRight, self.motorLeft, 55, 122)
        self.robotGiroscope = GyroSensor(Port.S2)

        self.driveSpeed = 100
        self.programmRunning = True
        self.map1 = map.getMap()
        self.center = map.getCenter()

    """
        Turns the robot by the specified angle. Using data from gyroscope sensor, to make curant turn.

        Parameters:
        - angle: The angle to turn in degrees.
    """

    def turn(self, angle):
        angle_way = angle / abs(angle)
        self.robotGiroscope.reset_angle(0)
        initial_angle = self.robotGiroscope.angle()

        while abs(abs(self.robotGiroscope.angle()) - initial_angle) < abs(angle):
            self.motorRight.run(100 * angle_way)
            self.motorLeft.run(-100 * angle_way)
            print(self.robotGiroscope.angle())

        self.motorLeft.brake()
        self.motorRight.brake()

    """
        Runs the robot until the end of the way to user.

        Parameters:
        - robotPosition_x: The x-coordinate of the robot.
        - robotPosition_y: The y-coordinate of the robot.
        - step: The step size to move (1 or -1).
    """

    def runUntilEnd(self, robotPosition_x, robotPosition_y, step):
        x = robotPosition_x
        y = robotPosition_y
        while self.map1[x][y + step] > 0:
            self.wheels.straight(200)
            y += step
        self.wheels.stop()
        return y

    """
        This method asks user to take coffi by clicking on the button 
    """

    def takeCoffi(self):
        self.coffiRobot.speaker.say("Click on button to take your coffi")
        flag = True
        while flag:
            if (self.robotBotton.pressed()):
                self.motorElevator.run(100)
                time.sleep(2.5)
                self.motorElevator.brake()
                flag = False

        time.sleep(2)
        self.coffiRobot.speaker.say("Click on button if you took coffi")
        flag = True
        while flag:
            if (self.robotBotton.pressed()):
                self.motorElevator.run(-100)
                time.sleep(2.5)
                self.motorElevator.brake()
                flag = False

    """
        Moves the robot back to the highway (middle way of the map).

        Parameters:
        - robotPosition_x: The x-coordinate of the robot.
        - robotPosition_y: The y-coordinate of the robot.
        - step: The step size to move (1 or -1).
    """

    def backToHighway(self, robotPosition_x, robotPosition_y, step):
        self.turn(180)
        x = robotPosition_x
        y = robotPosition_y
        while self.map1[x][y] != 0:
            self.wheels.straight(200)
            y += step
        self.wheels.stop()

    """
        Runs the main program to fulfill user orders.

        Parameters:
        - userOrdersGiven: List of user orders.
    """

    def runProgramm(self, userOrdersGiven):
        userOrders = userOrdersGiven
        robotGiroscopeLocal = GyroSensor(Port.S2)
        robotPosition_x = 0
        robotPosition_y = self.center
        angelLocal = 0

        while self.programmRunning:
            robotGiroscopeLocal.reset_angle(0)
            if self.map1[robotPosition_x][robotPosition_y + 1] in userOrders:
                print("left")
                self.turn(90)

                y = self.runUntilEnd(robotPosition_x, robotPosition_y, 1)

                self.takeCoffi()
                self.backToHighway(robotPosition_x, y, -1)

                userOrders.remove(self.map1[robotPosition_x][robotPosition_y + 1])

                if len(userOrders) != 0:
                    self.turn(90)
                else:
                    self.turn(-90)

            elif mapp.getMap()[robotPosition_x][robotPosition_y - 1] in userOrders:
                print("right")
                self.turn(-90)
                y = self.runUntilEnd(robotPosition_x, robotPosition_y, -1)

                self.takeCoffi()
                self.backToHighway(robotPosition_x, y, 1)

                userOrders.remove(self.map1[robotPosition_x][robotPosition_y - 1])

                if len(userOrders) != 0:
                    self.turn(-90)
                else:
                    self.turn(90)

            elif len(userOrders) == 0:
                print("Back")
                robotPosition_x = robotPosition_x - 1
                self.wheels.straight(200)
                self.wheels.stop()
                if robotPosition_x == 0:
                    self.coffiRobot.speaker.say("All users got coffi")
                    self.programmRunning = False
                angelLocal += 1

                if (abs(angelLocal) == 6):
                    self.turn((angelLocal / abs(angelLocal) * 1))
                    angelLocal = 0

            else:

                robotPosition_x = robotPosition_x + 1
                self.wheels.straight(200)
                self.wheels.stop()

                angelLocal += 1

                if (abs(angelLocal) == 6):
                    self.turn((angelLocal / abs(angelLocal) * (1)))
                    angelLocal = 0

# User inputs
# This data was used based on size of the class room, there we presented the robot.

# Lager kart
# length=1500
# wight= 720
# tableLength=280
# boards=9

rows = 75
columns = 36
center = 17
blockAria = (280 // 20) + 1
oneStep = 20
userPositions = [[168, 15, 9], [405, 15, 8], [665, 15, 7], [1170, 15, 6], [1270, 20, 5], [1010, 20, 4], [755, 20, 3],
                 [485, 20, 2], [230, 20, 1]]

finalStep = 1270 // oneStep + 1

userOrders = [1, 8]  # table number

mapp = Map(rows, columns, center, userPositions, blockAria, finalStep)
mapp.drawNewMap()
mapp.printMap()

app = Programm(mapp)
app.runProgramm(userOrders)
