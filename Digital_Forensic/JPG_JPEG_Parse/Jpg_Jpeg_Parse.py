# [ Re3ue ] JPG_JPEG_Parse.py

import os
import sys
import struct

class JPGJPEGParse :
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
        print("How to Use : python JPG_JPEG_Parse.py < JPG_JPEG File Path >")
        sys.exit(1)
    
    jpg_jpeg_file = sys.argv[1]
    parse = JPGJPEGParse(jpg_jpeg_file)
    parse.parse()
