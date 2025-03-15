# [ Re3ue ] AVI_Parse.py

import os
import sys
import struct

class AVIParse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

        # Elements
        self.list_list = []
        self.chunk_list = []
        
        # Codec
        self.codec_list = []
        self.vids_codec_list = []
        self.auds_codec_list = []

        # Video Data + Audio Data
        self.video_data_dictionary = {}
        self.audio_data_dictionary = {}
        self.video_data_file_path = os.getcwd() + "/Video_Data.bin"
        self.audio_data_file_path = os.getcwd() + "/Audio_Data.bin"
    
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
    AVI - Elements - List Chunk + Chunk
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
        print(f"[ DEBUG ] Chunks : {self.chunk_list}")

        print("\n========================================")

    """
    AVI - Elements - Chunk
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
    AVI - Elements - List Chunk
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
    AVI - Codec ( List )
    """
    def get_codec_list(self, f) :
        stream = []
        codec_list = []

        for chunk in self.chunk_list :
            if b'strh' in chunk :
                chunk_data = chunk[b'strh']
                # print(f"[ DEBUG ] Data of \"strh\" : {chunk_data}")

                chunk_size = chunk_data[0]
                chunk_offset = chunk_data[1]

                strh_data = self.get_chunk_data(f, chunk_size, chunk_offset)
                strh_type = strh_data[0:4]

                stream.append(strh_type)

            if b'strf' in chunk :
                chunk_data = chunk[b'strf']
                # print(f"[ DEBUG ] Data of \"strf\" : {chunk_data}")

                chunk_size = chunk_data[0]
                chunk_offset = chunk_data[1]

                strf_data = self.get_chunk_data(f, chunk_size, chunk_offset)

                stream.append(strf_data)
        
        codec_list = [stream[i:i+2] for i in range(0, len(stream), 2)]
        self.codec_list = codec_list

        # print(f"[ DEBUG ] Codecs : {self.codec_list}")
    
    """
    """
    def get_chunk_data(self, f, chunk_size, chunk_offset) :
        f.seek(chunk_offset)

        chunk_data = f.read(chunk_size)

        return chunk_data
    
    """
    AVI - Codec
    """
    def get_codec(self, f) :
        for codec in self.codec_list :
            # print(f"[ DEBUG ] Codec : {codec}")
            
            strh_type = codec[0]
            strf_data = codec[1]

            if strh_type == b'vids' :
                self.get_codec_vids(strf_data)
            
            if strh_type == b'auds' :
                self.get_codec_auds(strf_data)
            
            # ( ... ) => Chunk ID
    
    """
    AVI - Codec - "VIDS" ( Video ) : BITMAPINFOHEADER
    """
    def get_codec_vids(self, strf_data) :
        vids_format = [
            (0x00, "I", "biSize"),
            (0x04, "i", "biWidth"),
            (0x08, "i", "biHeight"),
            (0x0C, "H", "biPlanes"),
            (0x0E, "H", "biBitCount"),
            (0x10, "4s", "biCompression"),
            (0x14, "I", "biSizeImage"),
            (0x18, "i", "biXPelsPerMeter"),
            (0x1C, "i", "biYPelsPerMeter"),
            (0x20, "I", "biClrUsed"),
            (0x24, "I", "biClrImportant"),
        ]

        for field_offset, field_format, field_name in vids_format :
            field_size = struct.calcsize(field_format)
            field_data = struct.unpack_from(field_format, strf_data, field_offset)[0]

            # print(f"[ + ] {field_name} : {field_data}")

            if field_name == "biCompression" :
                codec_name = field_data

                self.vids_codec_list.append(codec_name)

                # print(f"[ DEBUG ] Codec Name : {codec_name}")

    """
    AVI - Codec - "AUDS" ( Audio ) : WAVEFORMATEX
    """
    def get_codec_auds(self, strf_data) :
        auds_format = [
            (0x00, "2s", "wFormatTag"),
            (0x02, "H", "nChannels"),
            (0x04, "I", "nSamplesPerSec"),
            (0x08, "I", "nAvgBytesPerSec"),
            (0x0C, "H", "nBlockAlign"),
            (0x0E, "H", "wBitsPerSample"),
            (0x10, "H", "cbSize"),
        ]

        for field_offset, field_format, field_name in auds_format :
            field_size = struct.calcsize(field_format)
            field_data = struct.unpack_from(field_format, strf_data, field_offset)[0]

            # print(f"[ + ] {field_name} : {field_data}")

            if field_name == "wFormatTag" :
                codec_name = field_data

                self.auds_codec_list.append(codec_name)
                
                # print(f"[ DEBUG ] Codec Name : {codec_name}")
    
    """
    AVI - ( Codec ) - Video Data
    """
    def get_video_data(self, f) :
        for chunk in self.chunk_list :
            for key in chunk :
                if key.endswith(b'dc') :
                    video_data_chunk = chunk[key]

                    video_data_size = video_data_chunk[0]
                    video_data_offset = video_data_chunk[1]

                    f.seek(video_data_offset)
                    video_data = f.read(video_data_size)

                    if key not in self.video_data_dictionary :
                        self.video_data_dictionary[key] = bytearray()
                    
                    self.video_data_dictionary[key].extend(video_data)

                    # print(f"[ DEBUG ] Video Data ( {key} ) : {video_data_size} | {video_data_offset}")
                    # print(f">>>> {video_data}")
        
        for key, video_data in self.video_data_dictionary.items() :
            video_data_file_path = self.video_data_file_path.replace(".bin", f"_{key.decode()}")
        
            with open(video_data_file_path, "wb") as vdf :
                vdf.write(video_data)
    
    """
    AVI - ( Codec ) - Audio Data
    """
    def get_audio_data(self, f) :
        for chunk in self.chunk_list :
            for key in chunk :   
                if key.endswith(b'wb') :
                    audio_data_chunk = chunk[key]

                    audio_data_size = audio_data_chunk[0]
                    audio_data_offset = audio_data_chunk[1]

                    f.seek(audio_data_offset)
                    audio_data = f.read(audio_data_size)

                    if key not in self.audio_data_dictionary :
                        self.audio_data_dictionary[key] = bytearray()

                    self.audio_data_dictionary[key].extend(audio_data)

                    # print(f"[ DEBUG ] Audio Data ( {key} ) : {audio_data_size} | {audio_data_offset}")
                    # print(f">>>> {audio_data}")
        
        for key, audio_data in self.audio_data_dictionary.items() :
            audio_data_file_path = self.audio_data_file_path.replace(".bin", f"_{key.decode()}")
        
            with open(audio_data_file_path, "wb") as adf :
                adf.write(audio_data)

    """
    AVI
    """
    def parse(self) :
        print("Program Start.")

        with open(self.file_path, "rb") as f :
            # RIFF
            self.get_riff(f)

            # Elements
            self.get_elements(f)

            # Codec
            self.get_codec_list(f)
            self.get_codec(f)

            # print(f"[ DEBUG ] \"vids\" Codec List : {self.vids_codec_list}")
            # print(f"[ DEBUG ] \"auds\" Codec List : {self.auds_codec_list}")

            # Video Data + Audio Data
            self.get_video_data(f)
            self.get_audio_data(f)

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
