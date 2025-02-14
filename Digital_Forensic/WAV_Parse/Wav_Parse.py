# [ Re3ue ] Wav_Parse.py

import os
import sys
import struct

class WAVParse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

    """
    """
    def parse(self) :
        print("Program Start.")

        print("\nProgram End.")

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python WAV_Parse.py < WAV File Path >")
        sys.exit(1)
    
    wav_file = sys.argv[1]
    parse = WAVParse(wav_file)
    parse.parse()
