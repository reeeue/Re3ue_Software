# [ Re3ue ] Fat32_Parse.py

import os
import sys
import struct

class FAT32Parse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python FAT32Parse.py < FAT32 File Path >")
        sys.exit(1)
    
    fat32_file = sys.argv[1]
    parse = FAT32Parse(fat32_file)
    parse.parse()
