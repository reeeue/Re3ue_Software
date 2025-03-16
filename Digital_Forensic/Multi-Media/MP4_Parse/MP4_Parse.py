# [ Re3ue ] MP4_Parse.py

import os
import sys
import struct

class MP4Parse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

        self.container_list = []
        self.box_list = []
    
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
    """
    def get_elements(self, f) :
        print("\nMP4 File - Elements")
        print("\n========================================")
        print()

        while True :
            box_type, box_size, box_offset = self.get_box(f)

            # End of File
            if box_type is None :
                break

            # Container Box
            if box_type in [b'moov', b'trak', b'mdia', b'minf', b'stbl'] :
                self.get_container(f, box_type, box_offset, box_size - 8, depth = 1)

            else :
                print(f"Box Type : {box_type.decode()}")
                print(f"[ + ] Box Size : {box_size}")
                print(f"[ + ] Box Offset : {self.print_hex(box_offset)}")

            # Next Box
            f.seek(box_offset - 8 + box_size)
        

        # print(f"[ DEBUG ] Container Boxes : {self.container_list}")
        # print(f"[ DEBUG ] Boxes : {self.box_list}")

        print("\n========================================")
    
    """
    """
    def get_box(self, f) :
        box_header = f.read(8)

        # End of File
        if len(box_header) < 8 :
            return None, None, None
        
        box_size, box_type = struct.unpack(">I4s", box_header) # Big Endian
        box_offset = f.tell()

        # List of Boxes : Not Container Box
        if box_type not in [b'moov', b'trak', b'mdia', b'minf', b'stbl'] :
            self.box_list.append({box_type : [box_size, box_offset]})

        return box_type, box_size, box_offset
    
    """
    """
    def get_container(self, f, box_type, box_offset, box_size, depth = 0) :
        f.seek(box_offset)

        end_offset = box_offset + box_size

        # List of Container Boxes : Container Box
        self.container_list.append({box_type : [box_size, box_offset]})

        space = self.print_space(depth - 1)
        print(f"\n{space}( Container ) Box Type : {box_type.decode()}")
        print(f"{space}[ + ] ( Container ) Box Size : {box_size}")
        print(f"{space}[ + ] ( Container ) Box Offset : {self.print_hex(box_offset)}")

        while f.tell() < end_offset :
            box_type, box_size, box_offset = self.get_box(f)

            # End of File
            if box_type is None :
                break

            # Container Box
            if box_type in [b'moov', b'trak', b'mdia', b'minf', b'stbl'] :
                self.get_container(f, box_type, box_offset, box_size - 8, depth + 1)

            else :
                space = self.print_space(depth)
                print(f"{space}Box Type : {box_type.decode()}")
                print(f"{space}[ + ] Box Size : {box_size}")
                print(f"{space}[ + ] Box Offset : {self.print_hex(box_offset)}")

            # Next Box
            f.seek(box_offset - 8 + box_size)
            
    """
    """
    def get_codec(self, f) :
        print()
    
    """
    MP4
    """
    def parse(self) :
        print("Program Start.")

        with open(self.file_path, "rb") as f :
            self.get_elements(f)

            self.get_codec(f)

            # ( ... )

        print("\nProgram End.")

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python MP4_Parse.py < MP4 File Path >")
        sys.exit(1)
    
    mp4_file = sys.argv[1]
    parse = MP4Parse(mp4_file)
    parse.parse()
