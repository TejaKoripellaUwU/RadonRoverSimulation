import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))


from copy import deepcopy
import math
from pathlib import Path
from Gamma_Ray_Code import GammaSim
from ThompsonSampling import PoseSampler
import json
import Constants
import GenerateSettings
import glob
import openmc

class EventHandler:
    def __init__(self,sampler:PoseSampler,sim:GammaSim) -> None:
        self.sim = sim
        self.sampler = sampler
        

    
    def default_exec(self, init_botpose, magnitude, batches):
        for i in range(batches):
            sim_results = self.sim.get_full_flux(self.sampler.current_pos)
            zero_counter = 0
            
            for f in [z[0][0]for z in sim_results["absorption"]]:
                if f == 0:
                    zero_counter +=1
                    
            if zero_counter == len(sim_results["absorption"]):
                return "Failed execution due to lack of particles"
            
            vector_theta = self.sampler.vector_based(sim_results)
            self.sampler.calculate_robot_pose(vector_theta, magnitude)

            print(f'batch {i+1} simulated')
        
        self.sampler.retrieve_best_guess_simple_avg()
        return "Successful Execution"
    
    def clear_debug(self):
        for i in glob.glob(str(Constants.debug_geometry_dir/"*")):
            os.remove(i)
        
            

if __name__ == "__main__":
   
    if not os.path.exists(Constants.simulation_meta_data_dir):
        os.mkdir(Constants.simulation_meta_data_dir)
    
    if (os.path.isfile(Constants.simulation_config_path)):
        response = input("geometry file detected would you like to reload settings (y/n)?")
        while response != ("y" and "n"):
            response = input("geometry file detected would you like to reload settings (y/n)?")
        if response == "y":
            GenerateSettings.main()
            
    with open(str(Constants.simulation_config_path),"r") as file:
        data = json.load(file)
        start_location = {"x":int(data["RobotStartX"]),"y":int(data["RobotStartY"])}
        batches = int(data["NumBatches"])
    
    m_sampler = PoseSampler(start_location)
    m_sim = GammaSim()
    m_sim.load_sim_config()
    m_handler = EventHandler(m_sampler,m_sim)
    m_handler.clear_debug()
    m_handler.default_exec(start_location,7,batches)
    