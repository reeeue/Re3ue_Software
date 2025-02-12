# [ Re3ue ] Gpt_Parse.py

import os
import sys
import struct

class GPTParse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python GPTParse.py < GPT File Path >")
        sys.exit(1)
    
    gpt_file = sys.argv[1]
    parse = GPTParse(gpt_file)
    parse.parse()
