import yaml
import io
import struct

from pathlib import Path

sfx_hashcd = "Sphinx/Sonix/SFX_Defines.h"
sfx_folder = "Sphinx/Binary/_bin_PC/_Eng"

print(sfx_hashcd, sfx_folder)

ht = {}

# swy: parse the hashcode defines from the correct SFX header file
with open(sfx_hashcd, 'r') as outfile:
    for line in outfile:
        line = line.split()
        if (len(line) < 3):
            continue
        
        if (line[0] == '#define'):
            # print(line)
            ht[int(line[2], 16)] = (line[1])

# print(ht)


data = dict(
    A = 'a',
    B = dict(
        C = 'c',
        D = 'd',
        E = 'e',
    )
)


# swy: iterate over all the soundbank files, make them human readable and unpack them
for file_path in Path(sfx_folder).glob('HC*.SFX'):
    hash = str(file_path).split('HC')[1].split('.')[0]
    hash = int(hash, 16)
    print(file_path, hash, ht[hash])
    with open(file_path, 'rb') as f:
        magic = struct.unpack('4s', f.read(4))[0]
        hashc = struct.unpack('<I', f.read(4))[0]
        offst = struct.unpack('<I', f.read(4))[0]
        fulls = struct.unpack('<I', f.read(4))[0]
        
        assert(magic == b'MUSX'), "unexpected header magic value, not MUSX."
        
        print(str(magic), hashc, offst, fulls)#, "%X" % magic)
        
        sfxstart               = struct.unpack('<I', f.read(4))[0]
        sfxlen                 = struct.unpack('<I', f.read(4))[0]
        
        sampleinfostart        = struct.unpack('<I', f.read(4))[0]
        sampleinfolen          = struct.unpack('<I', f.read(4))[0]
        
        specialsampleinfostart = struct.unpack('<I', f.read(4))[0]
        specialsampleinfolen   = struct.unpack('<I', f.read(4))[0]
        
        sampledatastart        = struct.unpack('<I', f.read(4))[0]
        sampledatalen          = struct.unpack('<I', f.read(4))[0]
        
        print(sfxstart, sfxlen, sampleinfostart, sampleinfolen, specialsampleinfostart, specialsampleinfolen, sampledatastart, sampledatalen)
        
        
        f.seek(sfxstart)
        
        sfxcount = struct.unpack('<I', f.read(4))[0]
        
        print(sfxcount)

    with open(ht[hash] + '.yml', 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)