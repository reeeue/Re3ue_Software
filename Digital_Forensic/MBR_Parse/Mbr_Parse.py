# [ Re3ue ] Mbr_Parse.py

import os
import sys
import struct

class MBRParse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python MBRParse.py < MBR File Path >")
        sys.exit(1)
    
    mbr_file = sys.argv[1]
    parse = MBRParse(mbr_file)
    parse.parse()
