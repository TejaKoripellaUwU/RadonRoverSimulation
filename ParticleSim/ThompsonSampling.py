import json
import math
import Constants
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))

from scipy.stats import beta

class PoseSampler():
    def __init__(self,init_botpose) -> None:
        self.botpose = init_botpose
        self.adjacency_list = [270,180,90,0]
        self.betas = None
        self.pos_history ={"travel_coords":[init_botpose],"best_guess":[]}
        self.current_pos = init_botpose

    
    def vector_based(self,input):
        absorption = [i[0][0]for i in input["absorption"]]
        maximum = (absorption[0],0)
        
        for index,element in enumerate(absorption):
            if element>maximum[0]:
                maximum = (element,index)
        if absorption[(maximum[1]+1)%4] > absorption[maximum[1]-1]:
            tangent_max = (absorption[(maximum[1]+1)%4],((maximum[1]+1)%4))
        else:
            tangent_max = (absorption[maximum[1]-1],maximum[1]-1)
        
        normalized_absorption_deg = (maximum[0]/(maximum[0]+tangent_max[0]))*90
        
        modified_adjacency_list = self.adjacency_list
        
        if (self.adjacency_list[maximum[1]] == 0 or self.adjacency_list[tangent_max[1]] == 0) and (self.adjacency_list[maximum[1]] == 270 or self.adjacency_list[tangent_max[1]] == 270):
            modified_adjacency_list = [270,180,90,0]
             
        if modified_adjacency_list[maximum[1]]>modified_adjacency_list[tangent_max[1]]: 
            final_deg_value = modified_adjacency_list[maximum[1]]-(90-normalized_absorption_deg)
        else: 
            final_deg_value = modified_adjacency_list[maximum[1]]+(90-normalized_absorption_deg)
            
        return final_deg_value
    
    def calculate_robot_pose(self,polar_degrees, magnitude):
        x = magnitude*math.cos(math.radians(polar_degrees))
        y = magnitude*math.sin(math.radians(polar_degrees))
        
        self.current_pos = {"x":self.current_pos["x"]+x,"y":self.current_pos["y"]+y}
        self.pos_history["travel_coords"].append(self.current_pos)
        
        self.update_pose_json()

        return self.pos_history
    
    def retrieve_best_guess_simple_avg(self):
        x = [p["x"] for p in self.pos_history["travel_coords"]]
        y = [p["y"] for p in self.pos_history["travel_coords"]]
        centroid = (sum(x) / len(self.pos_history["travel_coords"]), sum(y) / len(self.pos_history["travel_coords"]))
        self.pos_history["best_guess"] = centroid
        self.update_pose_json()
        return centroid
    
    def update_pose_json(self):
        with open(Constants.pos_log_path,"w") as position_log:
            position_log.write(json.dumps(self.pos_history))


    