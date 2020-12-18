import yaml
import io
import struct
import os
import collections

from pathlib import Path

sfx_folder = "Unpacked"

with open('HC00FFFF.SFX', 'rb') as f:
    magic = struct.unpack('4s', f.read(4))[0]
    hashc = struct.unpack('<I', f.read(4))[0]
    offst = struct.unpack('<I', f.read(4))[0]
    fulls = struct.unpack('<I', f.read(4))[0]
    
    assert(magic == b'MUSX'), "unexpected header magic value, not MUSX."
    assert(hashc == 0xFFFF),  "unexpected header hashcode, not 0xFFFF."
    
    print(' ', str(magic), hashc, offst, fulls)#, "%X" % magic)
    
    file_start1 = struct.unpack('<I', f.read(4))[0]
    filelength1 = struct.unpack('<I', f.read(4))[0]
    
    file_start2 = struct.unpack('<I', f.read(4))[0]
    filelength2 = struct.unpack('<I', f.read(4))[0]
    
    file_start3 = struct.unpack('<I', f.read(4))[0]
    filelength3 = struct.unpack('<I', f.read(4))[0]
    
    print(file_start1, filelength1, file_start2, filelength2, file_start3, filelength3)
    
    for i in range(0, int(filelength1 / 4)): # swy: size of one uint per element, actual counts are for scrubs
        f.seek(file_start1 + (i * 4))
        
        print("--", file_start1, i,file_start1 + i)
        markeroffset = struct.unpack('<I', f.read(4))[0]  # StreamLookupFileDetails
        
        print("  markeroffset: %x" % markeroffset, f.tell(), file_start2, markeroffset, file_start2 + markeroffset)
        
        f.seek(file_start2 + markeroffset)
        
        markersize   = struct.unpack('<I', f.read(4))[0]  # StreamLookupFileDetails2
        audio_offset = struct.unpack('<I', f.read(4))[0]
        audio_size   = struct.unpack('<I', f.read(4))[0]
        
        #Save current position
        orig_offset = f.tell()
        
        f.seek(audio_offset + 0x1000)
        
        #write file with data
        r = open("Unpacked/"+str(audio_offset)+".ima", "wb+")
        
        Data = f.read(audio_size)              
        r.write(Data)
        r.close()

        os.system('sox -t ima -e ima-adpcm -c 1 -r 22050 ' + 'Unpacked/'+str(audio_offset)+'.ima'  + ' -b 16 '+ 'Unpacked/'+str(audio_offset)+'.wav')
        
        #remove temporal .ima file
        os.remove("Unpacked/"+str(audio_offset)+".ima") 
        
        #Return to last position
        f.seek(orig_offset);
        print(" ", i, markersize, audio_offset, audio_size)
        
        startmarkercount  = struct.unpack('<I', f.read(4))[0] # MusicMarkerHeaderData
        markercount       = struct.unpack('<I', f.read(4))[0]
        startmarkeroffset = struct.unpack('<I', f.read(4))[0]
        markeroffset      = struct.unpack('<I', f.read(4))[0]
        basevolume        = struct.unpack('<I', f.read(4))[0]
        
        
        for j in range(0, startmarkercount):
        
            music_marker = {}
            music_marker[10] = 'MusicMarker_Start'
            music_marker[ 9] = 'MusicMarker_End'
            music_marker[ 7] = 'MusicMarker_Goto'
            music_marker[ 6] = 'MusicMarker_Loop'
            music_marker[ 5] = 'MusicMarker_Pause'
            music_marker[ 0] = 'MusicMarker_Jump'
            
            print(music_marker[0])
        
            name            = struct.unpack('<I', f.read(4))[0] # swy: embedded MusicMarkerData; don't ask me why this is stored twice afterwards; linear array seeking, probably
            pos             = struct.unpack('<I', f.read(4))[0]
            mtype           = struct.unpack('<I', f.read(4))[0]
            flags           = struct.unpack('<I', f.read(4))[0]
            extra           = struct.unpack('<I', f.read(4))[0]
            loopstart       = struct.unpack('<I', f.read(4))[0]
            markercount     = struct.unpack('<I', f.read(4))[0]
            loopmarkercount = struct.unpack('<I', f.read(4))[0]
        
            markerpos     = struct.unpack('<I', f.read(4))[0] # MusicMarkerStartData
            isinstant     = struct.unpack('<I', f.read(4))[0]
            instantbuffer = struct.unpack('<I', f.read(4))[0]
            state_a       = struct.unpack('<I', f.read(4))[0]
            state_b       = struct.unpack('<I', f.read(4))[0]
            
            
            print('    startmarkercount:', j, startmarkercount, '|', markerpos, name, pos, music_marker[int(mtype)], markercount, loopmarkercount)
        print(startmarkercount, markercount, startmarkeroffset, markeroffset, basevolume)