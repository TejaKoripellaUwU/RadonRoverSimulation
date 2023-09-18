from pathlib import Path

simulation_meta_data_dir = Path("../SimulationMetadata")
materials_xml_path = simulation_meta_data_dir/"materials.xml"
geometry_xml_path = simulation_meta_data_dir/"geometry.xml"
setting_xml_path = simulation_meta_data_dir/"settings.xml"
tallies_xml_path = simulation_meta_data_dir/"tallies.xml"
statepoint_h5_path = simulation_meta_data_dir/"statepoint.1.h5"
simulation_config_path = simulation_meta_data_dir/"universe_geometry.json"
load_xml_path = "load.xml"
