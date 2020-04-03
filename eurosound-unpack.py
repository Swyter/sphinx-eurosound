import yaml
import io
import struct
import os
import collections

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
        
        print(' ', str(magic), hashc, offst, fulls)#, "%X" % magic)
        
        sfxstart               = struct.unpack('<I', f.read(4))[0]
        sfxlen                 = struct.unpack('<I', f.read(4))[0]
        
        sampleinfostart        = struct.unpack('<I', f.read(4))[0]
        sampleinfolen          = struct.unpack('<I', f.read(4))[0]
        
        specialsampleinfostart = struct.unpack('<I', f.read(4))[0]
        specialsampleinfolen   = struct.unpack('<I', f.read(4))[0]
        
        sampledatastart        = struct.unpack('<I', f.read(4))[0]
        sampledatalen          = struct.unpack('<I', f.read(4))[0]
        
        print(' ', sfxstart, sfxlen, sampleinfostart, sampleinfolen, specialsampleinfostart, specialsampleinfolen, sampledatastart, sampledatalen)
        
        f.seek(sfxstart)
        
        sfx = []
        
        sfxcount = struct.unpack('<I', f.read(4))[0]

        print(' ', sfxcount, 'sound effects here')
        
        for i in range(0, sfxcount):
        
            f.seek(sfxstart + 4 + (i * 0x8))
            
            print("%x" % f.tell())
            
            hashcode        = struct.unpack('<I', f.read(4))[0]
            offset          = struct.unpack('<I', f.read(4))[0]
            
            hc_str = 0x1A000000 | hashcode
            
            if (hc_str in ht):
                hc_str = ht[hc_str]
            else:
                hc_str = "SFX_%#x" % hc_str
            
            print('  ', hashcode, hc_str, offset)
            
            sfx.append(hc_str)
            
            f.seek(sfxstart + offset)
            
            d = {}
            
            d['params'] = {}
            d['params']['duckerLength']      = struct.unpack('<H', f.read(2))[0]
            d['params']['minDelay']          = struct.unpack('<H', f.read(2))[0]
            d['params']['maxDelay']          = struct.unpack('<H', f.read(2))[0]
            d['params']['innerRadiusReal']          = struct.unpack('<H', f.read(2))[0]
            d['params']['outerRadiusReal']          = struct.unpack('<H', f.read(2))[0]
            d['params']['reverbSend']          = struct.unpack('<H', f.read(2))[0]
            d['params']['trackingType']          = struct.unpack('<H', f.read(2))[0]
            d['params']['maxVoices']          = struct.unpack('<H', f.read(2))[0]
            d['params']['priority']          = struct.unpack('<H', f.read(2))[0]
            d['params']['ducker']          = struct.unpack('<H', f.read(2))[0]
            d['params']['flags'] = {}
            
            flags = struct.unpack('<H', f.read(2))[0]
            
            d['params']['flags']['maxReject']          = (flags >>  0) & 1
            d['params']['flags']['nextFreeOneToUse']   = (flags >>  1) & 1
            d['params']['flags']['ignoreAge']          = (flags >>  2) & 1
            d['params']['flags']['multiSample']        = (flags >>  3) & 1
            d['params']['flags']['randomPick']         = (flags >>  4) & 1
            d['params']['flags']['shuffled']           = (flags >>  5) & 1
            d['params']['flags']['loop']               = (flags >>  6) & 1
            d['params']['flags']['polyphonic']         = (flags >>  7) & 1
            d['params']['flags']['underWater']         = (flags >>  8) & 1
            d['params']['flags']['pauseInNis']         = (flags >>  9) & 1
            d['params']['flags']['hasSubSfx']          = (flags >> 10) & 1
            d['params']['flags']['stealOnLouder']      = (flags >> 11) & 1
            d['params']['flags']['treatLikeMusic']     = (flags >> 12) & 1
            
            d['samples'] = {}
            
            
            if not os.path.exists(hc_str):
                os.mkdir(hc_str)
                
            with open(hc_str + '/effectProperties.yml', 'w') as outfile:
                outfile.write('# swy: EngineX sound effect exported from %s / %#x\n' % (hc_str, 0x1A000000 | hashcode))
                yaml.dump(d, outfile, default_flow_style=False, sort_keys=False)
                

    with open(ht[hash] + '.yml', 'w') as outfile:
        outfile.write('# swy: EngineX sound bank exported from %s / %#x\n' % (ht[hash], 0x1c000000 | hash))
        yaml.dump(sfx, outfile, default_flow_style=False, sort_keys=False)