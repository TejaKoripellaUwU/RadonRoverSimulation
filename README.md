# Design Document: GAYDARS (Gamma accumulation yield detector autonomous robot simulator):

Create a pygame simulation of a a robot navigating an enviornment to identify a single source of gamma radiation

Use OpenMC as a photon scatter simulation to track the number of high energy photons that intersect the detectors (geiger counters) using the flux tally

CSG generated geometry of the robot. the 4 purple rectangles represent the geiger counters and the yellow border represents lead to prevent interference from gamma rays counted multiple times

<img width="152" alt="image" src="https://github.com/TejaKoripellaUwU/RadonRoverSimulation/assets/73715703/f5711d3f-4159-4ceb-a4f4-ad4f4cc3ad26">

Use Bateman's equation to determine realistic isotope amounts in the radon decay chain

Use Thompson Sampling to determine a point for the robot toward

Use Pygame to create a semi-accurate simulation of the robot moving along these points


