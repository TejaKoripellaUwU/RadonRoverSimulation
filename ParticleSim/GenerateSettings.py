import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))

import Constants
from pathlib import Path

def main():
    print("Welcome to the Config generator!")
    init_botpose_x = input("What would you like the x component of the robot's pose to be? ")
    init_botpose_y = input("What would you like the y component of the robot's pose to be? ")
    init_sources_x = input("Where would you like the x component of the source to be located (max 35 euclidean units away from robot pose)? ")
    init_sources_y = input("Where would you like the y component of the source to be located (max 35 euclidean units away from robot pose)? ")
    init_robot_length = input("How long would you like the robot to be (7 inches default)? ")
    init_robot_width = input("How Wide would you like the robot to be (7 inches default)? ")
    num_batches = input("How many batches would you like the simulation to calculate (10 recommended)? ")

    simulation_config = {
        "RobotStartX":init_botpose_x,
        "RobotStartY":init_botpose_y,
        "UniverseSize": [75,75],
        "RobotSizeLength":init_robot_length,
        "RobotSizeWidth":init_robot_width,
        "SourceLocations":[[init_sources_x,init_botpose_y]],
        "NumBatches":num_batches
    }

    with open(Constants.universe_geometry_path,"w") as file:
        file.write(json.dumps(simulation_config))
        print("Config file written")

    