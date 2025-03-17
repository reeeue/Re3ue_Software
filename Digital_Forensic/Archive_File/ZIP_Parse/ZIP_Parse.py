# [ Re3ue ] Zip_Parse.py

import os
import sys
import struct

ECDR_SIGNATURE = b'\x50\x4B\x05\x06'
CDFH_SIGNATURE = b'\x50\x4B\x01\x02'
LFH_SIGNATURE = b'\x50\x4B\x03\x04'

class ZIPParse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

    """
    """
    def print_hex(self, int) :
        format = "0x" + f"{hex(int)[2:].upper()}"

        return format
    
    """
    """
    def get_ecdr(self, f) :
        f.seek(0, os.SEEK_END)

        file_size = f.tell()

        min_ecdr_size = 22
        max_ecdr_size = file_size

        ecdr_offset = -1
        buffer_size = 512

        for offset in range(file_size - min_ecdr_size, file_size - max_ecdr_size, -buffer_size) :
            f.seek(offset)

            data = f.read(min(buffer_size, file_size - offset))

            ecdr_signature_offset = data.rfind(ECDR_SIGNATURE)

            if ecdr_signature_offset == -1 :
                print("\n[ ERROR ] FAIL - ECDR Signature")
                print(f">>>>>>>>>> File Path : {self.file_path}")
                sys.exit(1)
            else :
                ecdr_signature_offset += offset 
                break
        
        f.seek(ecdr_signature_offset)

        ecdr_signature = f.read(4)
        ecdr_data = f.read(18)
        ecdr_fields = struct.unpack("<HHHHIIH", ecdr_data)

        ecdr_comment_length = ecdr_fields[6]

        if ecdr_comment_length > 0 :
            ecdr_comment_data = f.read(ecdr_comment_length)
            ecdr_comment_data_str = ecdr_comment_data.decode("utf-8", errors="ignore")
        else :
            ecdr_comment_data_str = ""

        print(f"[ + ] ECDR Signature ( Magic Number ) : ", " ".join(f"{byte:02X}" for byte in ecdr_signature))
        print(f"[ + ] Disk Number : {ecdr_fields[0]}")
        print(f"[ + ] Disk Number with Central Directory : {ecdr_fields[1]}")
        print(f"[ + ] Disk Entries in Disk : {ecdr_fields[2]}")
        print(f"[ + ] Total Entries in Central Directory : {ecdr_fields[3]}")
        print(f"[ + ] Central Directory Size : {ecdr_fields[4]}")
        print(f"[ + ] Offset of Start of Central Directory File Header : {ecdr_fields[5]}")
        print(f"[ + ] ECDR Comment Length : {ecdr_comment_length}")
        print(f"[ + ] ECDR Comment : {ecdr_comment_data_str}")

        return ecdr_fields[5] # Offset of Start of Central Directory File Header

    """
    """
    def get_cdfh(self, f, cdfh_offset) :
        f.seek(cdfh_offset)

        index = 0
        cd_file_list = []

        while True :
            current_offset = f.tell()

            cdfh_signature = f.read(4)

            if cdfh_signature != CDFH_SIGNATURE :
                print("\n[ ERROR ] FAIL - CDFH Signature")
                print(f">>>>>>>>>> File Path : {self.file_path}")
                print(f"{cdfh_signature}")
                sys.exit(1)
            
            cdfh_data = f.read(42)
            cdfh_fields = struct.unpack("<HHHHHHIIIHHHHHII", cdfh_data)

            file_name_length = cdfh_fields[9]
            extra_field_length = cdfh_fields[10]
            cdfh_comment_length = cdfh_fields[11]
            
            lfh_offset = cdfh_fields[15]

            file_name = f.read(file_name_length).decode("utf-8", errors="ignore")

            print(f"\n#{index} - Central Directory File Header")
            print(f"[ + ] CDFH Signature ( Magic Number ) : ", " ".join(f"{byte:02X}" for byte in cdfh_signature))
            print(f"[ + ] Version By : {cdfh_fields[0]}")
            print(f"[ + ] Version Need to Extract : {cdfh_fields[1]}")
            print(f"[ + ] General Purpose Bit Flag : {cdfh_fields[2]}")
            print(f"[ + ] Compression ( Method ) : {cdfh_fields[3]}")
            print(f"[ + ] Mod-Time / Mod-Date : {cdfh_fields[4]} / {cdfh_fields[5]}")
            print(f"[ + ] CRC-32 ( Check Sum ) : {cdfh_fields[6]:08X}")
            print(f"[ + ] Compressed Size / Un-Compressed Size : {cdfh_fields[7]} / {cdfh_fields[8]}")
            print(f"[ + ] File Name Length : {file_name_length}")
            print(f"[ + ] Extra Field Length : {extra_field_length}")
            print(f"[ + ] File Comment Length : {cdfh_comment_length}")
            print(f"[ + ] Disk Number of Start : {cdfh_fields[12]}")
            print(f"[ + ] Internal Attribute : {cdfh_fields[13]}")
            print(f"[ + ] External Attribute : {cdfh_fields[14]}")
            print(f"[ + ] Offset of Local File Header : {lfh_offset}")
            print(f"[ + ] File Name : {file_name}")

            cd_file_list.append((file_name, lfh_offset))

            index += 1

            f.seek(current_offset + 46 + file_name_length + extra_field_length + cdfh_comment_length, 0)
        
        return cd_file_list

    """
    """
    def get_lfh(self, f, index, lfh_offset) :
        f.seek(lfh_offset, 0)

        file_list = []

        lfh_signature = f.read(4)

        if lfh_signature != LFH_SIGNATURE :            
            print("\n[ ERROR ] FAIL - LFH Signature")
            print(f">>>>>>>>>> File Path : {self.file_path}")
            sys.exit(1)
        
        lfh_data = f.read(26)
        lfh_fields = struct.unpack("<HHHHHHHIIHH", lfh_data)

        file_name_length = lfh_fields[9]
        extra_field_length = lfh_fields[10]

        file_name = f.read(file_name_length).decode("utf-8", errors="ignore")

        print(f"\n#{index} - Local File Header")
        print(f"[ + ] LFH Signature ( Magic Number ) : ", " ".join(f"{byte:02X}" for byte in lfh_signature))
        print(f"[ + ] Version Need to Extract : {lfh_fields[0]}")
        print(f"[ + ] General Purpose Bit Flag : {lfh_fields[1]}")
        print(f"[ + ] Compression ( Method ) : {lfh_fields[2]}")
        print(f"[ + ] Mod-Time / Mod-Date : {lfh_fields[3]} / {lfh_fields[4]}")
        print(f"[ + ] CRC-32 ( Check Sum ) : {lfh_fields[5]}")
        print(f"[ + ] Compressed Size / Un-Compressed Size : {lfh_fields[6]} / {lfh_fields[7]}")
        print(f"[ + ] File Name Length : {file_name_length}")
        print(f"[ + ] Extra Field Length : {extra_field_length}")
        print(f"[ + ] File Name : {file_name}")

    """
    """
    def get_file_data(self, f) :
        print("\n# File Data")

        # To Do
    
    """
    """
    def parse(self) :
        print("Program Start.")

        with open(self.file_path, "rb") as f :

            # 1. End of Central Directory Record
            print("\n# End of Central Directory Record")
            cdfh_offset = self.get_ecdr(f)

            # 2. Central Directory Header
            print("\n# Central Directory File Header")
            print("\n========================================")
            cd_file_list = self.get_cdfh(f, cdfh_offset)
            print("\n========================================")

            # 3. Local File Header
            print("\n# Local File Header")
            print("\n========================================")
            for index, (file_name, lfh_offset) in enumerate(cd_file_list) :
                self.get_lfh(f, index, lfh_offset)
            print("\n========================================")

            # 4. File Data
            self.get_file_data(f)

        print("\nProgram End.")

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python ZIP_Parse.py < ZIP File Path >")
        sys.exit(1)
    
    zip_file = sys.argv[1]
    parse = ZIPParse(zip_file)
    parse.parse()
