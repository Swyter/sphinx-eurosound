import yaml
import io
import struct
import os
import collections
import sys

from pathlib import Path

sfx_hashcd = "X:\Sphinx\Sonix\SFX_Defines.h"
SFX_Defines = {}

def ReadHashcodesFile(FilePath):
    file = open(FilePath, "r")
    
    for line in file:
        SplittedLine = line.split()
        if (len(line) < 3) or line.startswith('/'):
            continue
        else:
            if SplittedLine[2] not in SFX_Defines:
                SFX_Defines[SplittedLine[2]] = SplittedLine[1]
                print("INFO -- New data added to the dictonary: %s, %s" % (SplittedLine[1], SplittedLine[2]))
            else:
                print("WARNING -- Trying to add data that already exists: %s %s"%(SplittedLine[1], SplittedLine[2]))
    
def GetHashcodeFromLabel(Label):
    hashc = ""
    for Hashcode, Value in SFX_Defines.items():
        if Value == Label:
            hashc = Hashcode
            print("INFO -- Requested Hashcode: %s"% Hashcode)
    if (len(hashc) < 1):
        print("WARNING -- Requested Hashcode (%s) has not found" % Label)
    return hashc

def GetFileName(Hashcode):
    NameHashcode = Hashcode[4:]
    NameWithExtension = ("HC%s.SFX"%NameHashcode)
    print("INFO -- The new file name is: %s" % NameWithExtension)
    
    return NameWithExtension

def RemoveSectionHashcode(Hashcode):
    Replace = "0x00"
    NewHashcode = Replace+Hashcode[4:]
     
    return NewHashcode
    
def GetSoundProps(File):
    Props = []
    Flags = []
    
    ReadingFlags = False
    document = yaml.full_load(File)
    for k, v in document['params'].items():
        if k == "flags":
            break
        Props.append(v)
    for k, v in document['params']['flags'].items():
        Flags.append(v)
   
    #Check flags
    bitfield = 0
    for i, flag in enumerate(Flags): 
        if flag is True:
            bitfield |= (1 << i)
    Props.append(bitfield)
    print(Props)
    
    return Props
    
#Check that we have arguments
if len(sys.argv) > 0:
    SoundBankFile = Path(sys.argv[1]).stem
    print("INFO -- SoundBank File: " + SoundBankFile)
    
    #Make a dictionary with the defined hashcodes.
    ReadHashcodesFile(sfx_hashcd)
    
    #Get the name of the new SFX file.
    Hashcode = GetHashcodeFromLabel(SoundBankFile)
    FileName = GetFileName(Hashcode)
    
    #Global offsets:
    sfxstart = 0x800
    
    #Create file    
    f = open(FileName, "wb")
    #Write MAGIC 
    f.write(struct.pack('4s', b"MUSX"))
    #Write Hash
    f.write(struct.pack('I', int(Hashcode,16)))
    #Write Offset
    f.write(struct.pack('I', int("0xC9",16)))
    #Write File full size
    f.write(struct.pack('I', int("0xC9",16))) #<-TEMP, wil be changed once the file be written.
   
    #Write SFX START
    f.write(struct.pack('I', sfxstart))
    
    #Store Folders to Check
    sfx = []
    
    #Read the sfx names of the list
    SoundsList = open(sys.argv[1], "r")
    for SoundFolder in SoundsList:
        if not SoundFolder.startswith('#'):
            Folder = SoundFolder.split()[1]
            sfx.append(Folder)
            print("INFO -- Folder to check: %s"%Folder)
    
    #Go to start position
    f.seek(sfxstart)
    
    #Write Number of SFX
    SfxCount = len(sfx)
    f.write(struct.pack('I', SfxCount))
    
    print ("INFO -- There are %d sound effects" % SfxCount)
    
    #Write sounds
    for i in range(len(sfx)):
        HashcodeToWrite = RemoveSectionHashcode(GetHashcodeFromLabel(sfx[i]))
        print("INFO -- The new hashcode is %s"%HashcodeToWrite)
        
        #Hashcode
        f.write(struct.pack('I', int(HashcodeToWrite,16)))
        
        #Open properties file
        PropertiesFilePath = "./"+sfx[i]+"/effectProperties.yml"
        File = open(PropertiesFilePath, "r")
        
        #Get array of sound properties
        SoundProperties = GetSoundProps(File)
        
        tracking_type = [
            '2D',
            'Amb',
            '3D',
            '3D_Rnd_Pos',
            '2D_PL2',
        ]
                
        #Write sound properties
        f.write(struct.pack('h',SoundProperties[0])) #duckerLength
        f.write(struct.pack('h',SoundProperties[1])) #minDelay
        f.write(struct.pack('h',SoundProperties[2])) #maxDelay
        f.write(struct.pack('h',SoundProperties[3])) #innerRadiusReal
        f.write(struct.pack('h',SoundProperties[4])) #outerRadiusReal
        f.write(struct.pack('b',SoundProperties[5])) #reverbSend
        f.write(struct.pack('b',tracking_type.index(SoundProperties[6]))) #trackingType
        f.write(struct.pack('b',SoundProperties[7])) #maxVoices
        f.write(struct.pack('b',SoundProperties[8])) #priority
        f.write(struct.pack('b',SoundProperties[9])) #ducker
        f.write(struct.pack('b',SoundProperties[10]))#masterVolume
        f.write(struct.pack('H',SoundProperties[11]))#Flags
        
        #Write number of samples
        
        #Foreach sample write properties
    f.close()