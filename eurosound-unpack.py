import yaml
import io
import struct

sfx_hashcd = "X:\\Sphinx\\Sonix\\SFX_Defines.h"
sfx_folder = "X:\\Sphinx\\Code\\PC\\_bin_PC\\_Eng"


print(sfx_hashcd, sfx_folder)

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