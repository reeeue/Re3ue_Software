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
    def __init__(self, file_path) :
        self.file_path = file_path

        self.chunks = []

    """
    """
    def get_true_crc(self, chunk_type, chunk_data, chunk_crc) :
        true_crc = zlib.crc32(chunk_type + chunk_data)

        return true_crc
    
    """
    """
    def get_png_header_signature(self, f) :
        png_header_signature = f.read(8)

        if png_header_signature != PNG_HEADER_SIGNATURE :
            print("\n[ ERROR ] FAIL - PNG ( Header ) Signature")
            print(f">>>>>>>>>> File Path : {self.file_path}")
            sys.exit(1)
        
        print(f"\n# PNG ( Header ) Signature")
        print(" ".join(f'{byte:02X}' for byte in png_header_signature))
    
    """
    """
    def get_png_footer_signature(self, f) :
        f.seek(-8, os.SEEK_END)

        png_footer_signature = f.read(8)

        if png_footer_signature != PNG_FOOTER_SIGNATURE :
            print("\n[ ERROR ] FAIL - PNG ( Footer ) Signature")
            print(f">>>>>>>>>> File Path : {self.file_path}")
            sys.exit(1)
        
        print(f"\n# PNG ( Footer ) Signature")
        print(" ".join(f'{byte:02X}' for byte in png_footer_signature))
    
    """
    """
    def get_chunk(self, f) :
        chunk_length = struct.unpack(">I", f.read(4))[0]
        chunk_type = f.read(4)
        chunk_data = f.read(chunk_length)
        chunk_crc = struct.unpack(">I", f.read(4))[0]

        chunk_name = chunk_type.decode()

        print(f"[ * ] Chunk - {chunk_name}")
        print(f"    [ + ] Chunk Length - {chunk_length}")
        print(f"    [ + ] Chunk Type - {chunk_type}")
        print(f"    [ + ] Chunk Data - {chunk_data}")
        print(f"    [ + ] Chunk CRC - {chunk_crc}")

        return chunk_length, chunk_type, chunk_data, chunk_crc, chunk_name

    """
    Chunk - IHDR : Color Type
    """
    def get_color_type(self, color_type_number) :
        color_types = {
            0 : "Gray Scale",
            2 : "RGB",
            3 : "Indexed Color ( Palette )",
            4 : "Gray Scale with Alph",
            6 : "RGB with Alpha"
        }

        return color_types.get(color_type_number, "Can't Find")

    """
    """
    def get_chunks(self, f) :
        print("\n# Chunks")

        chunk_list = []
        chunk_index = 1

        while True :
            chunk_length, chunk_type, chunk_data, chunk_crc, chunk_name = self.get_chunk(f)

            chunk_list.append(chunk_name)

            true_crc = self.get_true_crc(chunk_type, chunk_data, chunk_crc)

            crc_result = ( true_crc == chunk_crc )

            if crc_result == False :
                print("\n[ ERROR ] FAIL - CRC (Integrity)")
                print(f">>>>>>>>>> Chunk Index : {chunk_index}")
                print(f">>>>>>>>>> Chunk Name : {chunk_name}")
                print(f">>>>>>>>>> TRUE CRC : {true_crc}")
                print(f">>>>>>>>>> FALSE CRC ( In File ) : {chunk_crc}")
                sys.exit(1)

            if chunk_name == "IHDR" :
                width, height, bit_depth, color_type_number, compression_mothod, filter_method, interlace_method = struct.unpack(">IIBBBBB", chunk_data)

                color_type = self.get_color_type(color_type_number)

                print("  => Chunk Information - IHDR")
                print(f"    [ + ] Wdith : {width}")
                print(f"    [ + ] Height : {height}")
                print(f"    [ + ] Bit Depth : {bit_depth}")
                print(f"    [ + ] Color Type : {color_type_number} ( {color_type} )")
                print(f"    [ + ] Compression ( Method ) : {compression_mothod}")
                print(f"    [ + ] Filter ( Method ) : {filter_method}")
                print(f"    [ + ] Interlace ( Method ) : {interlace_method}")
            
            if chunk_name == "IEND" :
                print("\n# Chunk List")
                print(chunk_list)

                break
    
    """
    """
    def parse(self) :
        print("Program Start.")

        with open(self.file_path, "rb") as f :
            # 1. PNG ( Header ) Signature
            self.get_png_header_signature(f)

            # 2. Chunks
            self.get_chunks(f)

            # 3. PNG ( Footer ) Signature
            self.get_png_footer_signature(f)

        print("\nProgram End.")

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python PNG_Parse.py < PNG File Path >")
        sys.exit(1)
    
    png_file = sys.argv[1]
    parse = PNGParse(png_file)
    parse.parse()
