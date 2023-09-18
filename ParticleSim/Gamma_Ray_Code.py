# %%
from glob import glob
import math
from openmc import stats
import os
import numpy as np
import matplotlib.pyplot as plt
import openmc
import openmc.data
import numpy as np
from scipy.constants import Avogadro
from pathlib import Path
import radioactivedecay as rd
import json
import Constants

def get_decay_percentage(source,time,strength):
    source = rd.Inventory({source:strength},"Bq").decay(time,"h")
    return source.mass_fractions()

def bq_to_atoms(bq, half_life_seconds):
    decay_constant = np.log(2)/half_life_seconds
    return bq/decay_constant

def rd_to_mc(element:str):
    if element == "Pb-206":
        element = "Pb205_m1"
    return element.replace("-","")

def chunk_into_n(lst, n):
    size = math.ceil(len(lst) / n)
    return list(
        map(lambda x: lst[x * size:x * size + size],
        list(range(n)))
    )

def try_catch_simple(func):
    try:
        func()
    except Exception as e:
        pass


class GammaSim():
    def __init__(self) -> None:
        self.temp_graph = False
        self.radon_sources = []
        self.bot_size = {"Length":7, "Width":7}
        self.geiger_tube_radius = 1
        self.source_location = [-25,0,0]
        
    
    def define_mats(self):
        self.gas = openmc.Material(name="Gas")
        self.gas.add_element("Argon", 1)
        self.gas.set_density("g/cm3", 1)

        self.oxygen = openmc.Material(name = "Oxygen")
        self.oxygen.add_element("oxygen", 1)
        self.oxygen.set_density("g/cm3", 1)

        self.mats = openmc.Materials([self.gas,self.oxygen])
        self.mats.export_to_xml(str(Constants.materials_xml_path))
    
    def load_sim_config(self):
        with open(Constants.simulation_config_path,"r") as file:
            data = json.load(file)
            self.source_location = []
            for i in data["SourceLocations"][0]:
                self.source_location.append(int(i))
            self.source_location.append(0)
            # self.source_location = [int(*data["SourceLocations"][0]),0]
            self.bot_size = {"Length":int(data["RobotSizeLength"]),"Width":int(data["RobotSizeWidth"])}
        
    def create_geometry(self):

        self.allCells = []
        
        cyl_1 = openmc.XCylinder(y0=self.bot_pose["y"]-(self.bot_size["Width"]+self.geiger_tube_radius*2)/2,z0=0,r = self.geiger_tube_radius,boundary_type = "transmission")
        cyl_2 = openmc.YCylinder(x0=self.bot_pose["x"]-(self.bot_size["Length"]+self.geiger_tube_radius*2)/2,z0=0,r = self.geiger_tube_radius,boundary_type = "transmission")
        cyl_3 = openmc.XCylinder(y0=self.bot_pose["y"]+(self.bot_size["Width"]+self.geiger_tube_radius*2)/2,z0=0,r = self.geiger_tube_radius,boundary_type = "transmission")
        cyl_4 = openmc.YCylinder(x0=self.bot_pose["x"]+(self.bot_size["Length"]+self.geiger_tube_radius*2)/2,z0=0,r = self.geiger_tube_radius,boundary_type = "transmission")        

        plane_1 = openmc.XPlane(x0 = self.bot_pose["x"]-(self.bot_size["Length"])/2)
        plane_2 = openmc.XPlane(x0 = self.bot_pose["x"]+(self.bot_size["Length"])/2)
        plane_3 = openmc.YPlane(y0 = self.bot_pose["y"]-(self.bot_size["Width"])/2)
        plane_4 = openmc.YPlane(y0 = self.bot_pose["y"]+(self.bot_size["Width"])/2)
    
        ray_blocker_1 = openmc.rectangular_prism(axis = "z", width = self.bot_size["Length"], height = 1, origin = (self.bot_pose["x"],self.bot_pose["y"]-self.bot_size["Width"]/2),boundary_type="vacuum")
        ray_blocker_2 = openmc.rectangular_prism(axis = "z", width = 1, height = self.bot_size["Width"], origin = (self.bot_pose["x"]-self.bot_size["Length"]/2,self.bot_pose["y"]),boundary_type="vacuum")
        ray_blocker_3 = openmc.rectangular_prism(axis = "z", width = self.bot_size["Length"], height = 1, origin = (self.bot_pose["x"],self.bot_pose["y"]+self.bot_size["Width"]/2),boundary_type="vacuum")
        ray_blocker_4 = openmc.rectangular_prism(axis = "z", width = 1, height = self.bot_size["Width"], origin = (self.bot_pose["x"]+self.bot_size["Length"]/2,self.bot_pose["y"]),boundary_type="vacuum")

        self.cell_1 = openmc.Cell(cell_id = 10)
        self.cell_1.region = -cyl_1 & +plane_1 & -plane_2
        self.cell_1.fill = self.gas

        self.cell_2 = openmc.Cell(cell_id = 20)
        self.cell_2.region = -cyl_2 & +plane_3 & -plane_4
        self.cell_2.fill = self.gas

        self.cell_3 = openmc.Cell(cell_id = 30)
        self.cell_3.region = -cyl_3 & +plane_1 & -plane_2
        self.cell_3.fill = self.gas

        self.cell_4 = openmc.Cell(cell_id = 40)
        self.cell_4.region = -cyl_4 & +plane_3 & -plane_4
        self.cell_4.fill = self.gas

        self.allCells.append(self.cell_1)
        self.allCells.append(self.cell_2)
        self.allCells.append(self.cell_3)
        self.allCells.append(self.cell_4)

        blocker_cell_1 = openmc.Cell(region=ray_blocker_1)
        blocker_cell_2 = openmc.Cell(region=ray_blocker_2)
        blocker_cell_3 = openmc.Cell(region=ray_blocker_3)
        blocker_cell_4 = openmc.Cell(region=ray_blocker_4)

        outer_surface = openmc.Sphere(r=150.0)
        outer_surface.boundary_type = 'vacuum'

        inner_surface = openmc.Sphere(r=140.0)
        inner_surface.boundary_type = 'vacuum'

        empty_space = openmc.Cell()
        empty_space.region = -inner_surface & ~(-cyl_1 & +plane_1 & -plane_2) & ~(-cyl_2 & +plane_3 & -plane_4) & ~(-cyl_3 & +plane_1 & -plane_2) & ~(-cyl_4 & +plane_3 & -plane_4)
        empty_space.fill = self.oxygen
        
        universe = openmc.Universe(cells=[self.cell_1,self.cell_2, self.cell_3, self.cell_4,
                                          empty_space,
                                          blocker_cell_1,blocker_cell_2,blocker_cell_3,blocker_cell_4])
        self.geometry = openmc.Geometry(universe)
        self.geometry.export_to_xml(str(Constants.geometry_xml_path))
    
    def evaluate_sources(self):
        openmc.config['chain_file'] = Constants.load_xml_path
        print(self.source_location)
        self.init_radon_strength = 10000
        self.init_radon_time = 100*60*60

        RnSources_t0 = get_decay_percentage("Rn-222",self.init_radon_time,self.init_radon_strength)
    
        for index,element in enumerate(list(RnSources_t0.keys())):
            if element ==  "Ar-36":
                pass
            else:
                numAtoms = bq_to_atoms(self.init_radon_strength, 3.823 * 24 * 60 * 60) * RnSources_t0[element]
                self.radon_sources.append(openmc.Source())
                self.radon_sources[index].space = stats.Point(self.source_location)
                self.radon_sources[index].angle = stats.Isotropic()
                self.radon_sources[index].energy = openmc.data.decay_photon_energy(rd_to_mc(element))
                self.radon_sources[index].particle = 'photon'
                decayData = rd.DEFAULTDATA
                self.radon_sources[index].strength = (np.log(2)/decayData.half_life(nuclide = element)) * numAtoms

    def create_settings(self):
        self.settings = openmc.Settings()
        self.settings.particles = 5*10**4
        self.settings.batches = 1
        self.settings.photon_transport = True
        self.settings.source = [*self.radon_sources]
        self.settings.verbosity = 1
        self.settings.run_mode = 'fixed source'
        self.settings.export_to_xml(str(Constants.setting_xml_path))
    
    def define_tallies(self):
        
        self.tallies = openmc.Tallies()
        self.energy_bins = np.linspace(0, 1e6, 1001)
        
        energy_filter = openmc.EnergyFilter(self.energy_bins)
        cell_filter = openmc.CellFilter([i.id for i in self.allCells])
        particle_filter = openmc.ParticleFilter("photon")

        # energy_function_filter = openmc.EnergyFunctionFilter()

        pulse_tally = openmc.Tally(name='pulse-height')
        pulse_tally.filters = [cell_filter, energy_filter]
        pulse_tally.scores = ['pulse-height']

        absorption_tally = openmc.Tally(name="gamma_absorption")
        
        if self.temp_graph:absorption_tally.filters = [cell_filter,particle_filter,energy_filter]
        else: absorption_tally.filters = [cell_filter,particle_filter]
        
        absorption_tally.scores = ["flux"]


        # self.tallies.append(pulse_tally)
        self.tallies.append(absorption_tally)
        self.tallies.export_to_xml(str(Constants.tallies_xml_path))

    def get_flux(self):
        openmc.run(path_input=Constants.simulation_meta_data_dir,cwd=Constants.simulation_meta_data_dir)
        self.sp = openmc.StatePoint(Constants.statepoint_h5_path)
        absorption_data = self.sp.get_tally(name='gamma_absorption')
        return {"absorption": absorption_data.sum,"debugging": absorption_data}
    
    def run_sim(self):
        openmc.run(Constants.simulation_meta_data_dir)

        self.sp = openmc.StatePoint(Constants.statepoint_h5_path)
        pulse_data= self.sp.get_tally(name='pulse-height')
        absorption_data = self.sp.get_tally(name='gamma_absorption')
        pulse_height_values = chunk_into_n(pulse_data.get_values(scores=['pulse-height']).flatten(),len(self.allCells))
        
        absorption_values = chunk_into_n(absorption_data.get_values(scores=['flux']).flatten(),len(self.allCells))
            
        energy_bin_centers = self.energy_bins[1:] + 0.5 * (self.energy_bins[1] - self.energy_bins[0])
        for i in range(len(self.allCells)):
            plt.figure()
            plt.semilogy(energy_bin_centers[1:], pulse_height_values[i][1:])
            plt.xlabel('Energy [eV]')
            plt.ylabel('Counts')
            plt.title('Pulse Height Values')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"PulseHeight{i}")
            plt.close()
            plt.figure()
            plt.semilogy(energy_bin_centers[1:], absorption_values[i][1:])
            plt.xlabel('Energy [eV]')
            plt.ylabel('Photons/cm^2 - s')
            plt.title('Flux Values')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"Flux{i}")
            plt.close()


    def get_full_flux(self,bot_pose):
        self.bot_pose = bot_pose
        self.clean_workspace()
        self.define_mats()
        self.create_geometry()
        self.evaluate_sources()
        self.create_settings()
        self.define_tallies()
        data = self.get_flux()
        self.sp.close()
        self.clean_workspace()
        return data

        
    def clean_workspace(self):
        for file in glob(f"{str(Constants.simulation_meta_data_dir)}*.h5"):
            os.remove(file)
        for file in glob(f"{str(Constants.simulation_meta_data_dir)}*.out"):
            os.remove(file)
        try_catch_simple(lambda:os.remove(str(Constants.geometry_xml_path)))
        try_catch_simple(lambda:os.remove(str(Constants.materials_xml_path)))
        try_catch_simple(lambda:os.remove(str(Constants.setting_xml_path)))
        try_catch_simple(lambda:os.remove(str(Constants.tallies_xml_path)))


if __name__ == "__main__":
    g_sim = GammaSim()
    g_sim.get_full_flux({"x": -9.938664614578116, "y": 1.105868743989469})




# %%
