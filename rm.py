import glob
import os

for i in glob.glob("/root/ProjectFiles/ParticleSim/*png"):
    os.remove(i)
for i in glob.glob("/root/ProjectFiles/SimulationMetadata/*h5"):
    os.remove(i)