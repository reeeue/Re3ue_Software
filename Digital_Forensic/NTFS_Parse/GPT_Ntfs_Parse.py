# [ Re3ue ] GPT_Ntfs_Parse.py

import os
import sys
import struct

SECTOR_SIZE = 512

NTFS_OEM_ID = b"\x4E\x54\x46\x53\x20\x20\x20\x20"

VBR_SIGNATURE = b"\x55\xAA"
MFT_ENTRY_HEADER_SIGNATURE = b"FILE"

class NTFSParse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

        self.bytes_per_sector = 0
        self.sector_per_cluster = 0

        self.partition_start_sector = 0
        self.partition_start_offset = 0
        self.mft_start_sector = 0
        self.mft_start_offset = 0

        self.partition_list = []
        self.file_list = []
        self.deleted_file_list = []
    
    """
    """
    def print_hex(self, int) :
        format = "0x" + f"{hex(int)[2:].upper()}"

        return format

    """
    GPT - Protective MBR
    """
    def get_protective_mbr(self, f) :
        f.seek(446)

        partition_table_entry = f.read(16)

        partition_entry_table_fields = struct.unpack("<B3sB3sII", partition_table_entry)

        partition = {
            "boot_flag" : partition_entry_table_fields[0],
            "starting_chs_address" : partition_entry_table_fields[1],
            "partition_type" : partition_entry_table_fields[2],
            "ending_chs_address" : partition_entry_table_fields[3],
            "start_lba_address" : partition_entry_table_fields[4],
            "total_sectors_in_partition" : partition_entry_table_fields[5]
        }

        print(f"\n@GPT - Protective MBR")
        print(f"[ + ] Boot Flag : {self.print_hex(partition["boot_flag"])}")
        print(f"[ + ] Starting CHS Address : {self.print_hex(int.from_bytes(partition["starting_chs_address"], byteorder='little'))}")
        print(f"[ + ] Partition Type : {self.print_hex(partition["partition_type"])}")
        print(f"[ + ] Ending CHS Address : {self.print_hex(int.from_bytes(partition["ending_chs_address"], byteorder='little'))}")
        print(f"[ + ] Starting LBA Address : {self.print_hex(partition["start_lba_address"])} ( Sector )")
        print(f"[ + ] Total Sectors in Partition : {self.print_hex(partition["total_sectors_in_partition"])}")
        
    """
    GPT - ( Primary ) GPT Header
    """
    def get_gpt_header(self, f) :
        f.seek(SECTOR_SIZE)

        gpt_signature = f.read(8)

        gpt_header_data = f.read(84)
        gpt_header_fields = struct.unpack("<IIIIQQQQ16sQIII", gpt_header_data)

        revision = gpt_header_fields[0]
        header_size = gpt_header_fields[1]
        crc32_of_gpt_header = gpt_header_fields[2]
        reserved = gpt_header_fields[3]
        lba_of_gpt_header = gpt_header_fields[4]
        lba_of_backup_gpt_header = gpt_header_fields[5]
        starting_lba_of_partition = gpt_header_fields[6]
        ending_lba_of_partition = gpt_header_fields[7]
        disk_guid = gpt_header_fields[8]
        starting_lba_of_partition_entry_table = gpt_header_fields[9]
        number_of_partition_entry = gpt_header_fields[10]
        size_of_partition_entry = gpt_header_fields[11]
        crc32_of_partition_entry_table = gpt_header_fields[12]

        print(f"\n@GPT - ( Primary ) GPT Header")
        print(f"[ + ] GPT Signature : {gpt_signature}")
        print(f"[ + ] GPT Version : {revision}")
        print(f"[ + ] Size of GPT Header : {header_size}")
        print(f"[ + ] CRC-32 of GPT Header : {crc32_of_gpt_header}")
        print(f"[ + ] Reserved : {reserved}")
        print(f"[ + ] LBA of GPT Header : {lba_of_gpt_header} ( Sector )")
        print(f"[ + ] LBA of Back Up GPT Header : {lba_of_backup_gpt_header} ( Sector )")
        print(f"[ + ] Starting LBA of Partition : {starting_lba_of_partition} ( Sector )")
        print(f"[ + ] Ending LBA of Partition : {ending_lba_of_partition} ( Sector )")
        print(f"[ + ] Disk GUID : {self.print_hex(int.from_bytes(disk_guid, byteorder='little'))}")
        print(f"[ + ] Starting LBA of Partition Entry Table : {starting_lba_of_partition_entry_table}")
        print(f"[ + ] Number of Partition Entry : {number_of_partition_entry}")
        print(f"[ + ] Size of Partition Entry : {size_of_partition_entry} ( Byte )")
        print(f"[ + ] CRC-32 of Partition Entry Table : {crc32_of_partition_entry_table}")

        return starting_lba_of_partition_entry_table, number_of_partition_entry, size_of_partition_entry

    """
    GPT - Partition Entries
    """
    def get_gpt_partition_entries(self, f) :
        starting_lba_of_partition_entry_table, number_of_partition_entry, size_of_partition_entry = self.get_gpt_header(f)

        partition_entry_table_offset = starting_lba_of_partition_entry_table * SECTOR_SIZE
        f.seek(partition_entry_table_offset)

        partiton_entry_table_data_before = f.read(size_of_partition_entry * number_of_partition_entry)

        for index in range(number_of_partition_entry) :
            partition_entry_table_data = partiton_entry_table_data_before[index * size_of_partition_entry : (index + 1) * size_of_partition_entry]
        
            partition_entry_table_fields = struct.unpack("<16s16sQQQ72s", partition_entry_table_data)

            partition_type_guid = partition_entry_table_fields[0]
            unique_partition_guid = partition_entry_table_fields[1]
            starting_lba = partition_entry_table_fields[2]
            ending_lba = partition_entry_table_fields[3]
            attribute_flags = partition_entry_table_fields[4].to_bytes(8, byteorder='little')
            partition_name = partition_entry_table_fields[5].decode(errors='ignore')
            partition_size = (ending_lba - starting_lba + 1) * SECTOR_SIZE / (1024 * 1024)

            if starting_lba > 0 :
                print(f"\n@GPT - Partition Entry - #{index}")
                print(f"[ + ] Partition Type GUID : {self.print_hex(int.from_bytes(partition_type_guid, byteorder='little'))}")
                print(f"[ + ] Unique Partition GUID : {self.print_hex(int.from_bytes(unique_partition_guid, byteorder='little'))}")
                print(f"[ + ] Starting LBA : {starting_lba} ( Sector )")
                print(f"[ + ] Ending LBA : {ending_lba} ( Sector )")
                print(f"[ + ] Attribute Flags : {" ".join(f"{byte:02X}" for byte in (attribute_flags))}")
                print(f"[ + ] Partition Name : {partition_name}")
                print(f"[ + ] Partition Size : {partition_size} ( MB )")

                self.partition_list.append({
                    "Index" : index,
                    "Partition Type GUID" : partition_type_guid,
                    "Unique Partition GUID" : unique_partition_guid,
                    "First LBA" : starting_lba,
                    "Last LBA" : ending_lba,
                    "Attribute Flags" : attribute_flags,
                    "Partition Name" : partition_name,
                    "Partition Size" : partition_size
                })
        
        print(f"\n@GPT - Partition Entries")
        # print(f"Partitions : {self.partition_list}")
        print(f">>>> Total Number of Partitions : {len(self.partition_list)}")

    """
    GPT
    """
    def get_gpt(self, f) :
        print("\n# GPT")

        print("\n========================================")

        # [ 1 ] Protective MBR
        self.get_protective_mbr(f)

        # [ 2 + 3 ] ( Primary ) GPT Header + Partition Entries
        self.get_gpt_partition_entries(f)

        print("\n========================================")

    """
    NTFS
    """
    def get_ntfs(self, f) :
        print("\n# NTFS")

        print("\n========================================")

        print("\n========================================")
            
    """
    GPT_NTFS
    """
    def parse(self) :
        print("Program Start.")

        with open(self.file_path, "rb") as f :
            # [ 1 ] GPT
            self.get_gpt(f)
            # [ 2 ] NTFS
            self.get_ntfs(f)

        print("\nProgram End.")

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python GPT_Ntfs_Parse.py < ( GPT ) NTFS File Path >")
        sys.exit(1)
    
    ntfs_file = sys.argv[1]
    parse = NTFSParse(ntfs_file)
    parse.parse()
