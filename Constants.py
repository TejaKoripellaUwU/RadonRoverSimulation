from pathlib import Path
import os

root_dir = Path(os.getcwd())
visuals_dir = root_dir/"Visuals"
simulation_meta_data_dir = root_dir/"SimulationMetadata"
materials_xml_path = simulation_meta_data_dir/"materials.xml"
geometry_xml_path = simulation_meta_data_dir/"geometry.xml"
setting_xml_path = simulation_meta_data_dir/"settings.xml"
tallies_xml_path = simulation_meta_data_dir/"tallies.xml"
statepoint_h5_path = simulation_meta_data_dir/"statepoint.1.h5"
universe_geometry_path = simulation_meta_data_dir/"universe_geometry.json"
pos_log_path = simulation_meta_data_dir/"position_data.json"
debug_geometry_dir = visuals_dir/"Debug"
graphs_folder = visuals_dir/"Graphs"
load_xml_path = root_dir/"load.xml"
