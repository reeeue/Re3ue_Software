# [ Re3ue ] Png_Parse.py

import os
import sys

class PNGParse :
    def __init__(self, filePath) :
        self.filePath = filePath
    
    def parse(self) :
        print("Program Start.")

        with open(self.filePath, "rb") as f :
            # 1. PNG Signature
            self.get_png_signature(f)
            # 2. Chunks
            self.get_chunks(f)

        print("Program End.")
    
    def get_png_signature(self, f) :
        print("# PNG Signature")
    
    def get_chunks(self, f) :
        print("# Chunks")

    def get_chunk(self, f) :
        print("# Chunk")

if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python PNGParse.py < PNG File Path >")
        sys.exit(1)
    
    png_file = sys.argv[1]
    parse = PNGParse
    parse.parse()
