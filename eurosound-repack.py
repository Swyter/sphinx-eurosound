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
    #Write CRC32 Check
    f.write(struct.pack('I', int("0xC9",16))) #<-TEMP, wil be changed once the file be written.
    #Write SFX START
    f.write(struct.pack('I', sfxstart))
    
    SoundsList = open(sys.argv[1], "r")
    for SoundFolder in SoundsList:
        if not SoundFolder.startswith('#'):
            Folder = SoundFolder.split()[1]
            print("INFO -- Folder to check: %s"%Folder)
    
    
    #Go to start position
    f.seek(sfxstart)
    f.write(struct.pack('4s', b"TEST"))
    f.close()