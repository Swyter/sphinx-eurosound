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

print('[+] loading stream file')


streams = {}

with open(sfx_folder + '/HC00FFFF.SFX', 'rb') as f:
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
#quit()

def get_sample(sb_file, sample_ref, sampleinfostart, sampleinfolen, sampledatastart, sampledatalen):
    orig_offset = sb_file.tell()
    print('   ', 'get_sample(', sb_file, sample_ref, sampleinfostart, sampleinfolen, sampledatastart, sampledatalen)
    
    sb_file.seek(sampleinfostart + 4 + (sample_ref * 0x28))
    
    si = {}
    si['flags']            = struct.unpack('<I', sb_file.read(4))[0]
    si['address']          = struct.unpack('<I', sb_file.read(4))[0]
    si['size']             = struct.unpack('<I', sb_file.read(4))[0]
    si['frequency']        = struct.unpack('<I', sb_file.read(4))[0]
    si['realsize']         = struct.unpack('<I', sb_file.read(4))[0]
    si['numberofchannels'] = struct.unpack('<I', sb_file.read(4))[0]
    si['bitsperchannel']   = struct.unpack('<I', sb_file.read(4))[0]
    si['psi_sampleheader'] = struct.unpack('<I', sb_file.read(4))[0]
    si['loopoffset']       = struct.unpack('<I', sb_file.read(4))[0]
    si['duration']         = struct.unpack('<I', sb_file.read(4))[0]
    
    si['bitsperchannel'] = 16
    
    
    print("%#x" % sb_file.tell(), sample_ref)
    
    sb_file.seek(sampledatastart + si['address'])
    
    print("%#x" % sb_file.tell(), si)
    
    si['data']             = sb_file.read(si['realsize'])

    sb_file.seek(orig_offset);
    return si

global_sfx = []
sb = {}

# swy: iterate over all the soundbank files, make them human readable and unpack them
for file_path in Path(sfx_folder).glob('HC*.SFX'):
    break
    hash = str(file_path).split('HC')[1].split('.')[0]
    hash = int(hash, 16)
    
    #if (not str(file_path).endswith('HC00000A.SFX')):
    #    continue
    
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
        
        f.seek(sampleinfostart)
        samplecount            = struct.unpack('<I', f.read(4))[0]        
        
        print(' ', sfxstart, sfxlen, sampleinfostart, sampleinfolen, specialsampleinfostart, specialsampleinfolen, sampledatastart, sampledatalen)
        
        f.seek(sfxstart)
        
        sb[hashc] = []
        sfx = []
        
        sfxcount = struct.unpack('<I', f.read(4))[0]

        print(' ', sfxcount, 'sound effects here')
        
        for i in range(0, sfxcount):
        
            f.seek(sfxstart + 4 + (i * 0x8)) # swy: the 4 is for the sfxcount size
            
            hashcode        = struct.unpack('<I', f.read(4))[0]
            offset          = struct.unpack('<I', f.read(4))[0]
            
            hc_str = 0x1A000000 | hashcode
            
            if (hc_str in ht):
                hc_str = ht[hc_str]
            else:
                hc_str = "SFX_%#x" % hc_str
            
            print('  ', hashcode, hc_str, offset)
            
            sfx.append(hc_str)
            sb[hashc].append(hashcode)

            continue
            
            # swy: skip sound effects that we have already dumped in this session, even if they are from other soundbanks;
            #      ideally they should all be the same, so we save time
            if (hc_str in global_sfx):
                continue
                
            global_sfx.append(hc_str)
            
            f.seek(sfxstart + offset)
            
            tracking_type = [
                '2D',
		        'Amb',
		        '3D',
		        '3D_Rnd_Pos',
		        '2D_PL2',
            ]
            
            d = {}
            
            d['params'] = {}
            d['params']['duckerLength']    = struct.unpack('<h', f.read(2))[0]
            d['params']['minDelay']        = struct.unpack('<h', f.read(2))[0]
            d['params']['maxDelay']        = struct.unpack('<h', f.read(2))[0]
            d['params']['innerRadiusReal'] = struct.unpack('<h', f.read(2))[0]
            d['params']['outerRadiusReal'] = struct.unpack('<h', f.read(2))[0]
            d['params']['reverbSend']      = struct.unpack('<b', f.read(1))[0]
            d['params']['trackingType']    = tracking_type[ struct.unpack('<b', f.read(1))[0] ]
            d['params']['maxVoices']       = struct.unpack('<b', f.read(1))[0]
            d['params']['priority']        = struct.unpack('<b', f.read(1))[0]
            d['params']['ducker']          = struct.unpack('<b', f.read(1))[0]
            d['params']['masterVolume']    = struct.unpack('<b', f.read(1))[0]
            d['params']['flags'] = {}
            
            flags = struct.unpack('<H', f.read(2))[0]
            
            d['params']['flags']['maxReject']          = bool((flags >>  0) & 1)
            d['params']['flags']['nextFreeOneToUse']   = bool((flags >>  1) & 1)
            d['params']['flags']['ignoreAge']          = bool((flags >>  2) & 1)
            d['params']['flags']['multiSample']        = bool((flags >>  3) & 1)
            d['params']['flags']['randomPick']         = bool((flags >>  4) & 1)
            d['params']['flags']['shuffled']           = bool((flags >>  5) & 1)
            d['params']['flags']['loop']               = bool((flags >>  6) & 1)
            d['params']['flags']['polyphonic']         = bool((flags >>  7) & 1)
            d['params']['flags']['underWater']         = bool((flags >>  8) & 1)
            d['params']['flags']['pauseInNis']         = bool((flags >>  9) & 1)
            d['params']['flags']['hasSubSfx']          = bool((flags >> 10) & 1)
            d['params']['flags']['stealOnLouder']      = bool((flags >> 11) & 1)
            d['params']['flags']['treatLikeMusic']     = bool((flags >> 12) & 1)
            
            
            if not os.path.exists('SFX/' + hc_str):
                os.mkdir('SFX/' + hc_str)
            
            sample_count    = struct.unpack('<h', f.read(2))[0]
            d['samples'] = {}
            
            for j in range(0, sample_count):
            
                s = {}
                s['fileRef']             = struct.unpack('<h', f.read(2))[0]
                s['pitchOffset']         = struct.unpack('<h', f.read(2))[0]
                s['randomPitchOffset']   = struct.unpack('<h', f.read(2))[0]
                s['baseVolume']          = struct.unpack('<b', f.read(1))[0]
                s['randomVolumeOffset']  = struct.unpack('<b', f.read(1))[0]
                s['pan']                 = struct.unpack('<b', f.read(1))[0]
                s['randomPan']           = struct.unpack('<b', f.read(1))[0]
                
                f.read(2) # s16 PadEm, don't ask me about alignment
                
                d['samples'][j] = s
                
                # swy: ignore streamed (negative indexed) sounds for now
                if s['fileRef'] < 0:
                    continue
                    
                    
                if s['fileRef'] >= samplecount:
                    print(" [!] fileRef %u out of bounds (max is %u) at offset %#x; ignoring." % (s['fileRef'], samplecount - 1, f.tell()))
                    continue
                    
                si = get_sample(f, s['fileRef'], sampleinfostart, sampleinfolen, sampledatastart, sampledatalen)

                with open('SFX/' + hc_str + '/' + chr(ord('a') + j) + '.wav', 'wb') as wavfile:
                    wavfile.write(b'RIFF')               # chunk_id
                    wavfile.write(struct.pack('<I', ((44 - 8) + si['realsize']) )) # chunk_size
                    wavfile.write(b'WAVE')               # format
                    
                    wavfile.write(b'fmt ')               # subchunk_id
                    wavfile.write(struct.pack('<I', 16)) # subchunk_size: 16; size of the rest
                    wavfile.write(struct.pack('<H',  1)) # audio_format: WAV_FORMAT_PCM
                    wavfile.write(struct.pack('<H', si['numberofchannels'])) # num_channels
                    wavfile.write(struct.pack('<I', si['frequency'])) # sample_rate
                    wavfile.write(struct.pack('<I', int(si['frequency'] * si['numberofchannels'] * si['bitsperchannel'] / 8))) # byte_rate
                    wavfile.write(struct.pack('<H',                   int(si['numberofchannels'] * si['bitsperchannel'] / 8))) # block_align
                    wavfile.write(struct.pack('<H', si['bitsperchannel'])) # bits_per_sample
                    
                    wavfile.write(b'data')               # subchunk_id
                    wavfile.write(struct.pack('<I', si['realsize']))  # subchunk_size
                    
                    wavfile.write(si['data'])
                
            with open('SFX/' + hc_str + '/effectProperties.yml', 'w') as outfile:
                outfile.write('# swy: EngineX sound effect exported from %s / %#x\n' % (hc_str, 0x1A000000 | hashcode))
                yaml.dump(d, outfile, default_flow_style=False, sort_keys=False)
        #

        continue

        if not os.path.exists('SB/'):
            os.mkdir('SB/')
        #
        with open('SB/' + ht[hash] + '.yml', 'w') as outfile:
            outfile.write('# swy: EngineX sound bank exported from %s / %#x\n' % (ht[hash], 0x1c000000 | hash))
            yaml.dump(sfx, outfile, default_flow_style=False, sort_keys=False)

#with open('__all.yml', 'w') as outfile:
#    uniq_sfx = {}
#    # swy: sort the SFX by hashcode, they are usually sorted by hashcode label on export.
#    for cur_sb in sb:
#        sb[cur_sb].sort()
#
#        for cur_sfx in sb[cur_sb]:
#            uniq_sfx[cur_sfx] = { 'lst_prev': None, 'lst_next': None, 'lst_prev_matches': None, 'lst_next_matches': None }
#
#    uniq_sfx = dict(sorted(uniq_sfx.items()))
#    yaml.dump(sb, outfile, default_flow_style=False, sort_keys=False)


with open('__all.yml', 'r') as infile:
    sb = yaml.safe_load(infile)
    uniq_sfx = {}
    # swy: sort the SFX by hashcode, they are usually sorted by hashcode label on export.
    for cur_sb in sb:
        sb[cur_sb].sort()

        for cur_sfx in sb[cur_sb]:
            uniq_sfx[cur_sfx] = { 'lst_prev': None, 'lst_next': None, 'lst_prev_matches': None, 'lst_next_matches': None, 'counter': 0, 'sb': {} }

    for cur_sb in sb:
        cur_sb_last_index = len(sb[cur_sb]) - 1
        for idx, cur_sfx in enumerate(sb[cur_sb]):
            prev_sfx = None; next_sfx = None
            if (idx - 1) > 0:
                prev_sfx = sb[cur_sb][idx - 1]

            if (idx + 1) <= cur_sb_last_index:
                next_sfx = sb[cur_sb][idx + 1]

            if cur_sfx == 88:
                i=1

            uniq_sfx[cur_sfx]['sb'][cur_sb] = [prev_sfx, next_sfx]

            if prev_sfx:
                test = uniq_sfx[cur_sfx]['lst_prev'] == prev_sfx
                if uniq_sfx[cur_sfx]['lst_prev'] and uniq_sfx[cur_sfx]['lst_prev_matches'] != False:
                    uniq_sfx[cur_sfx]['lst_prev_matches'] = test
                uniq_sfx[cur_sfx]['lst_prev'] = prev_sfx

            if next_sfx:
                test = uniq_sfx[cur_sfx]['lst_next'] == next_sfx
                if uniq_sfx[cur_sfx]['lst_next'] and uniq_sfx[cur_sfx]['lst_next_matches'] != False:
                    uniq_sfx[cur_sfx]['lst_next_matches'] = test
                uniq_sfx[cur_sfx]['lst_next'] = next_sfx

            hc_str = 0x1A000000 | cur_sfx
            
            if (hc_str in ht):
                hc_str = ht[hc_str]
            else:
                hc_str = "SFX_%#x" % hc_str

            uniq_sfx[cur_sfx]['counter'] += 1
            uniq_sfx[cur_sfx]['hc'] = hc_str

    uniq_sfx = dict(sorted(uniq_sfx.items()))

    with open('__uniq.yml', 'w') as outfile:
        yaml.dump(uniq_sfx, outfile, default_flow_style=False, sort_keys=False)


    with open('__uniq.dot', 'w') as outfile:
        for cur_sfx in uniq_sfx:
            for idx in uniq_sfx[cur_sfx]['sb']:
                if uniq_sfx[cur_sfx]['sb'][idx][0]:
                    outfile.write(f"{cur_sfx} -> {uniq_sfx[cur_sfx]['sb'][idx][0]}\n")
                if uniq_sfx[cur_sfx]['sb'][idx][1]:
                    outfile.write(f"{cur_sfx} -> {uniq_sfx[cur_sfx]['sb'][idx][1]}\n")