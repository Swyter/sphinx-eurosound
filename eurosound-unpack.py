import yaml
import io
import struct

sfx_hashcd = "Sphinx/Sonix/SFX_Defines.h"
sfx_folder = "Sphinx/Binary/_bin_PC/_Eng"


print(sfx_hashcd, sfx_folder)

ht = {}

with open(sfx_hashcd, 'r') as outfile:
    for line in outfile:
        line = line.split()
        if (len(line) < 3):
            continue
        
        if (line[0] == '#define'):
            print(line)
            ht[int(line[2], 16)] = (line[1])

print(ht)

data = dict(
    A = 'a',
    B = dict(
        C = 'c',
        D = 'd',
        E = 'e',
    )
)

with open('data.yml', 'w') as outfile:
    yaml.dump(data, outfile, default_flow_style=False)