# [ Re3ue ] AVI_Parse.py

import os
import sys
import struct

class AVIParse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

        self.list_list = []
        self.chunk_list = []
        
        self.codec_list = []
    
    """
    """
    def print_hex(self, int) :
        format = "0x" + f"{hex(int)[2:].upper()}"

        return format
    
    """
    """
    def print_space(self, depth) :
        space = "      " * depth
        
        return space
    
    """
    AVI - RIFF Header
    """
    def get_riff(self, f) :
        riff_header = f.read(12)

        group_id, file_size, file_type = struct.unpack("<4sI4s", riff_header)

        if group_id != b'RIFF' :
            print("\n[ ERROR ] FAIL - RIFF Header ( RIFF )")
            print(f">>>>>>>>>> File Path : {self.file_path}")
            print(f"{group_id}")
            sys.exit(1)

        print("\n#0 RIFF Header")
        print(f"[ + ] File Size : {file_size}")
        print(f"[ + ] File Type : {file_type.decode()}")
    
    """
    """
    def get_elements(self, f) :
        print("\nAVI File - Elements")
        print("\n========================================")

        while True :
            chunk_id, chunk_size, chunk_offset = self.get_chunk(f)

            # End of File
            if chunk_id is None :
                break

            # List Chunk
            if chunk_id == b'LIST' :
                self.get_list(f, chunk_offset, chunk_size, depth = 1)

            else :
                print(f"Chunk ID : {chunk_id.decode()}")
                print(f"[ + ] Chunk Size : {chunk_size}")
                print(f"[ + ] Chunk Offset : {self.print_hex(chunk_offset)}")
            
            # Next Chunk
            f.seek(chunk_offset + chunk_size)

        # print(f"[ DEBUG ] List Chunks : {self.list_list}")
        # print(f"[ DEBUG ] Chunks : {self.chunk_list}")

        print("\n========================================")

    """
    """
    def get_chunk(self, f) :
        chunk_header = f.read(8)

        # End of File
        if len(chunk_header) < 8 :
            return None, None, None
        
        chunk_id, chunk_size = struct.unpack("<4sI", chunk_header) # Little Endian

        if chunk_size % 2 == 0 :
            chunk_offset = f.tell()
        else :
            chunk_offset = f.tell() + 1

        # List of Chunks : Not List Chunk
        if chunk_id != b'LIST' :
            self.chunk_list.append({chunk_id : [chunk_size, chunk_offset]})

        return chunk_id, chunk_size, chunk_offset
    
    """
    """
    def get_list(self, f, list_offset, list_size, depth = 0) :
        f.seek(list_offset)

        end_offset = list_offset + list_size

        list_type = f.read(4)

        # List of List Chunks : List Chunk
        self.list_list.append({list_type : [list_size, list_offset]})

        space = self.print_space(depth - 1)
        print(f"\n{space}List Type : {list_type.decode()}")
        print(f"{space}[ + ] Chunk Size : {list_size}")
        print(f"{space}[ + ] Chunk Offset : {self.print_hex(list_offset)}")

        while f.tell() < end_offset :
            chunk_id, chunk_size, chunk_offset = self.get_chunk(f)

            # End of File
            if chunk_id is None :
                break

            # List Chunk
            if chunk_id == b'LIST' :
                self.get_list(f, chunk_offset, chunk_size, depth + 1)

            else :
                space = self.print_space(depth)
                print(f"{space}Chunk ID : {chunk_id.decode()}")
                print(f"{space}[ + ] Chunk Size : {chunk_size}")
                print(f"{space}[ + ] Chunk Offset : {self.print_hex(chunk_offset)}")
            
            # Next Chunk
            f.seek(chunk_offset + chunk_size)
    
    """
    """
    def get_codec(self, f) :
        print()

    """
    AVI
    """
    def parse(self) :
        print("Program Start.")

        with open(self.file_path, "rb") as f :
            self.get_riff(f)

            self.get_elements(f)

            self.get_codec(f)

            # ( ... )

        print("\nProgram End.")

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python AVI_Parse.py < AVI File Path >")
        sys.exit(1)
    
    avi_file = sys.argv[1]
    parse = AVIParse(avi_file)
    parse.parse()
