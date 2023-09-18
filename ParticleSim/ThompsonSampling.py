from scipy.stats import beta

class PoseSampler():
    def __init__(self,num_machines) -> None:
        self.adjacency_list = [270,180,90,0]
        self.num_machines = num_machines
        self.betas = None
        
    def simple_greedy(self,input):
        return max(input)
    
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
                
    def create_beta_distributions(self):
        for i in range(len(self.num_machines)):
            self.betas[i] = beta()
    