# [ Re3ue ] Png_Parse.py

import os
import sys
import struct
import zlib

PNG_HEADER_SIGNATURE = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A' # 8 Bytes
PNG_FOOTER_SIGNATURE = b'\x49\x45\x4E\x44\xAE\x42\x60\x82' # 8 Bytes

class PNGParse :
    """
    """
    def __init__(self, filePath) :
        self.filePath = filePath
        self.chunks = []
    
    """
    """
    def parse(self) :
        print("Program Start.")

        with open(self.filePath, "rb") as f :
            # 1. PNG ( Header ) Signature
            self.get_png_header_signature(f)
            # 2. Chunks
            self.get_chunks(f)
            # 3. PNG ( Footer ) Signature
            self.get_png_footer_signature(f)

        print("Program End.")
    
    """
    """
    def get_png_header_signature(self, f) :
        png_header_signature = f.read(8)

        if png_header_signature != PNG_HEADER_SIGNATURE :
            print("[ ERROR ] FAIL - PNG ( Header ) Signature")
            print(f">>>>>>>>>> File Path : {self.filePath}")
            sys.exit(1)
        
        print(f"# PNG ( Header ) Signature")
        print("".join(f'{byte:02X}' for byte in png_header_signature))
    
    """
    """
    def get_png_footer_signature(self, f) :
        f.seek(-8, os.SEEK_END)
        png_footer_signature = f.read(8)

        if png_footer_signature != PNG_FOOTER_SIGNATURE :
            print("[ ERROR ] FAIL - PNG ( Footer ) Signature")
            print(f">>>>>>>>>> File Path : {self.filePath}")
            sys.exit(1)
        
        print(f"# PNG ( Footer ) Signature")
        print("".join(f'{byte:02X}' for byte in png_footer_signature))

    """
    """
    def get_chunks(self, f) :
        print("# Chunks")

        chunk_list = []
        chunk_index = 1

        while True :
            chunk_length, chunk_type, chunk_data, chunk_crc, chunk_name = self.get_chunk(f)

            chunk_list.append(chunk_name)

            crc_result = self.get_crc_result(chunk_type, chunk_data, chunk_crc)

            if crc_result == False :
                print("[ ERROR ] FAIL - CRC (Integrity)")
                print(f">>>>>>>>>> Chunk Index : {chunk_index}")
                print(f">>>>>>>>>> Chunk Name : {chunk_name}")
                sys.exit(1)
            
            if chunk_name == "IEND" :
                print("# Chunk List")
                print(chunk_list)

                break
            
    """
    """
    def get_chunk(self, f) :
        chunk_length = struct.unpack(">I", f.read(4))[0]
        chunk_type = f.read(4)
        chunk_data = f.read(chunk_length)
        chunk_crc = struct.unpack(">I", f.read(4))[0]

        chunk_name = chunk_type.decode()

        print(f"# Chunk - {chunk_name}")

        return chunk_length, chunk_type, chunk_data, chunk_crc, chunk_name

    """
    """
    def get_crc_result(self, chunk_type, chunk_data, chunk_crc) :
        crc = zlib.crc32(chunk_type + chunk_data)

        return crc == chunk_crc

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python PNGParse.py < PNG File Path >")
        sys.exit(1)
    
    png_file = sys.argv[1]
    parse = PNGParse(png_file)
    parse.parse()
