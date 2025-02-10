# [ Re3ue ] Zip_Parse.py

import os
import sys

class ZIPParse :
    def __init__(self, filePath) :
        self.filePath = filePath

    def parse(self) :
        print("Program Start.")

        with open(self.filePath, "rb") as f :
            # 1. End of Central Directory Record
            self.get_eocd_record(f)
            # 2. Central Directory Header
            self.get_cd_header(f)
            # 3. Local File Header
            self.get_lf_header(f)
            # 4. File Data
            self.get_file_data(f)

        print("Program End.")
    
    def get_eocd_record(self, f) :
        print("# End of Central Directory Record")
    
    def get_cd_header(self, f) :
        print("# Central Directory File Header")
    
    def get_lf_header(self, f) :
        print("# Local File Header")
    
    def get_file_data(self, f) :
        print("# File Data")

if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python ZIPParse.py < ZIP File Path >")
        sys.exit(1)
    
    pe_file = sys.argv[1]
    parse = ZIPParse(pe_file)
    parse.parse()
