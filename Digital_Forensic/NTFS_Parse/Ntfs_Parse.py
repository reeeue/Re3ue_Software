# [ Re3ue ] Ntfs_Parse.py

import os
import sys
import struct

class NTFSParse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python NTFSParse.py < NTFS File Path >")
        sys.exit(1)
    
    ntfs_file = sys.argv[1]
    parse = NTFSParse(ntfs_file)
    parse.parse()
