import pandas as pd
from copy import deepcopy

travel_coords= [
        {
            "x": 0,
            "y": 0
        },
        {
            "x": 8.247810215690654,
            "y": 7.278298334497486
        },
        {
            "x": 16.851297781614758,
            "y": 14.132494254004701
        },
        {
            "x": 25.1724090022933,
            "y": 21.326874564573338
        },
        {
            "x": 21.528041820538068,
            "y": 17.331405165179824
        },
        {
            "x": 28.140990636530773,
            "y": 20.55507365247658
        },
        {
            "x": 26.827609087476258,
            "y": 17.58131127380024
        },
        {
            "x": 28.60569474977268,
            "y": 18.49695933803447
        },
        {
            "x": 28.24404576174811,
            "y": 16.529928578371365
        },
        {
            "x": 29.86876660717984,
            "y": 17.696239932350057
        },
        {
            "x": 29.786099258204526,
            "y": 15.697949135340425
        },
        {
            "x": 28.036433574251436,
            "y": 13.709939654668462
        },
        {
            "x": 29.889757932803196,
            "y": 14.461730065620015
        },
        {
            "x": 31.36230500372567,
            "y": 16.404346629061116
        },
        {
            "x": 29.92835523557187,
            "y": 15.01014862934527
        },
        {
            "x": 28.24640424590059,
            "y": 16.804847033730763
        }
    ]
total_flux =  [
        0.002608436421965191,
        0.006154599246225919,
        0.01976743277971867,
        0.09245763844496124,
        0.06796394032757094,
        0.15380441369228967,
        0.7957789160603663,
        0.7482289461163375,
        0.42152360099851904,
        2.1638624698130307,
        0.18880010930707994,
        0.4749827102216425,
        0.2051152984355652,
        0.3536978670916839,
        0.20328056195149788
    ]

x = [p["x"] for p in travel_coords]
y = [p["y"] for p in travel_coords]
print(len(total_flux))
print(len(travel_coords))
numRem = 0 
for index,val in enumerate(total_flux):
    
    if 1/(2*val) > 7:
        x.pop(index-numRem)
        y.pop(index-numRem)
        numRem += 1

centroid = (sum(x) / len(x), sum(y) / len(y))

print(centroid)
    