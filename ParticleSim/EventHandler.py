from copy import deepcopy
import math
from pathlib import Path
from Gamma_Ray_Code import GammaSim
from ThompsonSampling import PoseSampler
import json
import Constants
import GenerateSettings
import openmc
import os

class EventHandler:
    def __init__(self,sampler:PoseSampler,sim:GammaSim,root_path:Path) -> None:
        self.sim = sim
        self.sampler = sampler
        self.current_pos = None
        self.pos_log_path = root_path/"position_data.json"
        self.pos_history = []
        
    def calculate_robot_pose(self,polar_degrees, magnitude):
        x = magnitude*math.cos(math.radians(polar_degrees))
        y = magnitude*math.sin(math.radians(polar_degrees))
        
        self.current_pos = {"x":self.current_pos["x"]+x,"y":self.current_pos["y"]+y}
        self.pos_history.append(self.current_pos)
        
        with open(self.pos_log_path,"w") as position_log:
            position_log.write(json.dumps(self.pos_history))
        return self.current_pos
    
    def default_exec(self, init_botpose, magnitude, batches):
        self.pos_history.append(init_botpose)
        self.current_pos = init_botpose

        for i in range(batches):
            sim_results = self.sim.get_full_flux(self.current_pos)
            zero_counter = 0
            
            for f in [z[0][0]for z in sim_results["absorption"]]:
                if f == 0:
                    zero_counter +=1
                    
            if zero_counter == len(sim_results["absorption"]):
                return "Failed execution due to lack of particles"
            
            vector_theta = self.sampler.vector_based(sim_results)
            self.calculate_robot_pose(vector_theta, magnitude)
            print(f'batch{i} simulated')
        return "Successful Execution"
        
            

if __name__ == "__main__":
    root_path = Path("../SimulationMetadata")
    
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
    
    print(root_path)
    m_sampler = PoseSampler(4)
    m_sim = GammaSim()
    m_sim.load_sim_config()
    m_handler = EventHandler(m_sampler,m_sim,root_path)
    m_handler.default_exec(start_location,3,batches)