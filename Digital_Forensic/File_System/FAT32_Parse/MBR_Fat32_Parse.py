# [ Re3ue ] Fat32_Parse.py

import os
import sys
import struct

MBR_SIGNATURE = b"\x55\xAA"
BOOT_SECTOR_SIGNATURE = b"\x55\xAA"
FSINFO_SIGNATURE_1 = b"\x52\x52\x61\x41"
FSINFO_SIGNATURE_2 = b"\x72\x72\x41\x61"
FSINFO_SIGNATURE_3 = b"\x55\xAA"

class FAT32Parse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

        self.bytes_per_sector = 0
        self.sectors_per_cluster = 0
        self.sectors_per_track = 0

        self.partition_fat32_sector = 0
        self.partition_fat32_offset = 0
        self.reserved_area_sector = 0
        self.reserved_area_offset = 0
        self.fat_area_sector = 0
        self.fat_area_offset = 0
        self.data_area_sector = 0
        self.data_area_offset = 0

        self.root_directory_cluster = 0
        self.root_directory_sector = 0
        self.root_directory_offset = 0

        self.file_list = []
    
    """
    """
    def print_hex(self, int) :
        format = "0x" + f"{hex(int)[2:].upper()}"

        return format
    
    """
    MBR
    """
    def get_mbr(self, f) :
        print("\n# MBR")

        print("\n========================================")

        f.seek(0)

        boot_code = f.read(446)
        partition_table_entries = f.read(64)
        mbr_signature = f.read(2)

        if mbr_signature != MBR_SIGNATURE :
            print("\n[ ERROR ] FAIL - MBR Signature ( 55 AA )")
            print(f">>>>>>>>>> File Path : {self.file_path}")
            sys.exit(1)

        partition_list = []
        
        for index in range(4) :
            offset = 16 * index
            
            partition_table_entry = partition_table_entries[offset:offset+16]

            partition_table_entry_fields = struct.unpack("<BBHB3sII", partition_table_entry)
            
            partition = {
                "boot_flag" : partition_table_entry_fields[0],
                "chs_address" : partition_table_entry_fields[1],
                "starting_chs_address" : partition_table_entry_fields[2],
                "partition_type" : partition_table_entry_fields[3],
                "ending_chs_address" : int.from_bytes(partition_table_entry_fields[4], byteorder='little'),
                "starting_lba_address" : partition_table_entry_fields[5],
                "size_in_sector" : partition_table_entry_fields[6]
            }

            print(f"\n@ Partition - #{index}")
            print(f"Boot Flag : {self.print_hex(partition["boot_flag"])}")
            print(f"CHS Address : {self.print_hex(partition["chs_address"])}")
            print(f"Startind CHS Address : {self.print_hex(partition["starting_chs_address"])}")
            print(f"Partition Type : {self.print_hex(partition["partition_type"])}")
            print(f"Ending CHS Address : {self.print_hex(partition["ending_chs_address"])}")
            print(f"Starting LBA Address : {self.print_hex(partition["starting_lba_address"])} ( Sector )")
            print(f"Total Sectors ( Size in Sector ) : {self.print_hex(partition["size_in_sector"])}")
    
            partition_list.append(partition)
        
        print("\n========================================")

        # print(f"[ DEBUG ] Partition List : {partition_list}")

        return partition_list

    """
    FAT32 - Reserved Area - Boot Sector - BPB
    """
    def get_bpb(self, bpb_data) :
        # print("\n# FAT32 - Reserved Area - Boot Sector - BPB")

        oem_id = bpb_data[0:8]

        bpb_fields = struct.unpack("<QHBHBHHBHHHIIIHHIHH12sBBBI11sQ", bpb_data)
        
        bytes_per_sector = bpb_fields[1]
        sectors_per_cluster = bpb_fields[2]
        reserved_sector_count = bpb_fields[3]
        number_of_fat_tables = bpb_fields[4]
        root_directory_entry_count = bpb_fields[5]
        total_sector_16 = bpb_fields[6] # 0000
        media_type = bpb_fields[7]
        fat_size_16 = bpb_fields[8] # 0000
        sectors_per_track = bpb_fields[9]
        number_of_heads = bpb_fields[10]
        hidden_sectors = bpb_fields[11]
        total_sector_32 = bpb_fields[12]
        fat_size_32 = bpb_fields[13]
        ext_flags = bpb_fields[14]
        fat32_volume_version = bpb_fields[15]
        root_directory_cluster_offset = bpb_fields[16]
        fsinfo_offset = bpb_fields[17]
        backup_boot_sector_offset = bpb_fields[18]
        reserved = bpb_fields[19]
        int_0x13_drive_number = bpb_fields[20]
        drive_number_reserved = bpb_fields[21]
        boot_signature = bpb_fields[22]
        volume_serial_number = bpb_fields[23]
        volume_label = bpb_fields[24]
        file_system_type = bpb_fields[25]

        print(f"[ + ] OEM ID ( STR / HEX ) : {oem_id.decode(errors='errors')} / {" ".join(f"{byte:02X}" for byte in oem_id)}")
        print(f"[ + ] Bytes Per Sector : {bytes_per_sector}")
        print(f"[ + ] Sectors Per Cluster : {sectors_per_cluster}")
        print(f"[ + ] Reserved Sector Count : {self.print_hex(reserved_sector_count)}")
        print(f"    ( ... )")
        print(f"[ + ] Sectors Per Track : {sectors_per_track}")
        print(f"    ( ... )")
        print(f"[ + ] FAT32 Size : {fat_size_32}")
        print(f"    ( ... )")
        print(f"[ + ] Root Directory Cluster Offset : {self.print_hex(root_directory_cluster_offset)} ( Cluster )")
        print(f"    ( ... )")

        self.bytes_per_sector = bytes_per_sector
        self.sectors_per_cluster = sectors_per_cluster
        self.sectors_per_track = sectors_per_track

        self.fat_area_sector = self.reserved_area_sector + reserved_sector_count
        self.fat_area_offset = self.fat_area_sector * self.bytes_per_sector
        
        self.backup_fat_area_sector = self.fat_area_sector + fat_size_32
        self.backup_fat_area_offset = self.backup_fat_area_sector * self.bytes_per_sector

        self.data_area_sector = self.fat_area_sector + (fat_size_32 * 2)
        self.data_area_offset = self.data_area_sector * self.bytes_per_sector

        self.root_directory_cluster = root_directory_cluster_offset
        self.root_directory_sector = self.data_area_sector + (root_directory_cluster_offset - 2) * self.sectors_per_cluster
        self.root_directory_offset = self.root_directory_sector * self.bytes_per_sector

        return fsinfo_offset

    """
    FAT32 - Reserved Area - Boot Sector
    """
    def get_boot_sector(self, f) :
        # print("\n# FAT32 - Reserved Area - Boot Sector")

        f.seek(self.reserved_area_offset)

        # print(f"[ DEBUG ] Boot Sector Offset : {self.partition_fat32_offset}")
        # print(f"[ DEUBG ] Offset : {f.tell()}")

        jump_command = f.read(3)
        bpb = f.read(87)
        boot_code = f.read(420)
        boot_sector_signature = f.read(2)

        if boot_sector_signature != BOOT_SECTOR_SIGNATURE :
            print("\n[ ERROR ] FAIL - Boot Sector Signature ( 55 AA )")
            print(f">>>>>>>>>> File Path : {self.file_path}")
            print(f"{boot_sector_signature}")
            sys.exit(1)
        
        print(f"[ + ] Jump Command to Boot Code : {" ".join(f"{byte:02X}" for byte in jump_command)}")
        print("    ( ... )")
        # print(f"[ + ] BPB : {bpb}")
        # print(f"[ + ] Boot Code : {boot_code}")
        # print(f"[ + ] Boot Sector Signature : {" ".join(f"{byte:02X}" for byte in boot_sector_signature)}")
    
        fsinfo_offset = self.get_bpb(bpb)

        return fsinfo_offset
    
    """
    FAT32 - Reserved Area - FSINFO
    """
    def get_fsinfo(self, f, fsinfo_offset) :
        # print("\n# FAT32 - Reserved Area - FSINFO")

        f.seek((self.partition_fat32_offset) + (fsinfo_offset * self.bytes_per_sector))
        
        # print(f"[ DEBUG ] FSINFO Sector Offset : {(self.partition_fat32_offset) + (fsinfo_offset * self.bytes_per_sector)}")
        # print(f"[ DEUBG ] Offset : {f.tell()}")

        fsinfo_signature_1 = f.read(4)
        fsinfo_reserved_1 = f.read(480)
        fsinfo_signature_2 = f.read(4)
        number_of_free_clusters = f.read(4)
        next_free_cluster = f.read(4)
        fsinfo_reserved_2 = f.read(14)
        fsinfo_signature_3 = f.read(2)

        if fsinfo_signature_1 != FSINFO_SIGNATURE_1 :
            print("\n[ ERROR ] FAIL - FSINFO Signature #1 ( RRaA )")
            print(f">>>>>>>>>> File Path : {self.file_path}")
            print(f">>>>>>>>>> {fsinfo_signature_1}")
            sys.exit(1)

        if fsinfo_signature_2 != FSINFO_SIGNATURE_2 :
            print("\n[ ERROR ] FAIL - FSINFO Signature #2 ( rrAa )")
            print(f">>>>>>>>>> File Path : {self.file_path}")
            sys.exit(1)
        
        if fsinfo_signature_3 != FSINFO_SIGNATURE_3 :
            print("\n[ ERROR ] FAIL - FSINFO Signature #3 ( 55 AA )")
            print(f">>>>>>>>>> File Path : {self.file_path}")
            sys.exit(1)
        
        print(f"[ + ] FSINFO Signature #1 : {fsinfo_signature_1}")
        print(f"    ( ... )")
        print(f"[ + ] FSINFO Signature #2 : {fsinfo_signature_2}")
        print(f"    ( ... )")
        print(f"[ + ] Number of Free Clusters : {self.print_hex(int.from_bytes(number_of_free_clusters, byteorder='little'))}")
        print(f"[ + ] Next Free Cluster : {self.print_hex(int.from_bytes(next_free_cluster, byteorder='little'))}")
        print(f"    ( ... )")

    """
    FAT32 - Reserved Area
    """
    def get_reserved_area(self, f) :
        print("\n# FAT32 - Reserved Area")
        print(f"  >>>> Sector : {self.reserved_area_sector}\n")

        fsinfo_offset = self.get_boot_sector(f)
        self.get_fsinfo(f, fsinfo_offset)
    
    """
    """
    def parse(self) :
        print("Program Start.")

        with open(self.file_path, "rb") as f :
            # [ 0-1 ] MBR
            partition_list = self.get_mbr(f)

            for index, partition in enumerate(partition_list) :

                # [ 0-2 ] Partition - FAT32
                if partition["partition_type"] == 0x0B or partition["partition_type"] == 0x0C :
                    print(f"\n@ Partition - #{index}")

                    self.partition_fat32_sector = partition["starting_lba_address"]
                    self.partition_fat32_offset = self.partition_fat32_sector * 512

                    # [ 1 ] Reserved Area
                    self.reserved_area_sector = self.partition_fat32_sector
                    self.reserved_area_offset = self.partition_fat32_offset
                    self.get_reserved_area(f)

        print("\nProgram End.")

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python MBR_FAT32_Parse.py < ( MBR ) FAT32 File Path >")
        sys.exit(1)
    
    fat32_file = sys.argv[1]
    parse = FAT32Parse(fat32_file)
    parse.parse()
