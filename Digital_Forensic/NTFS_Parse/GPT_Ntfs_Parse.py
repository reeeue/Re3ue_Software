# [ Re3ue ] Ntfs_Parse.py

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

        print(f"\n@GPT - Protective MBR")
        print(f"[ + ] Boot Flag : {self.print_hex(partition["boot_flag"])}")
        print("    ( ... )")
        print(f"[ + ] Starting LBA Address : {self.print_hex(partition["starting_lba_address"])} ( Sector )")
        print(f"[ + ] Total Sectors ( Size in Sector ) : {self.print_hex(partition["size_in_sector"])}")
        
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
        crc32_of_header = gpt_header_fields[2]
        reserved = gpt_header_fields[3]
        lba_of_gpt_header = gpt_header_fields[4]
        lba_of_backup_gpt_header = gpt_header_fields[5]
        starting_lba_for_partition = gpt_header_fields[6]
        ending_lba_for_partition = gpt_header_fields[7]
        disk_guid = gpt_header_fields[8]
        partition_table_entry_starting_lba = gpt_header_fields[9]
        number_of_partition_entries = gpt_header_fields[10]
        size_of_partition_entry = gpt_header_fields[11]
        crc32_of_partition_table = gpt_header_fields[12]

        print(f"\n@GPT - ( Primary ) GPT Header")
        print(f"[ + ] GPT Signature : {gpt_signature}")
        print("    ( ... )")
        print(f"[ + ] LBA of GPT Header : {lba_of_gpt_header} ( Sector )")
        print(f"[ + ] LBA of Back Up GPT Header : {lba_of_backup_gpt_header} ( Sector )")
        print(f"[ + ] Starting LBA for Partition : {starting_lba_for_partition} ( Sector )")
        print(f"[ + ] Ending LBA for Partition : {ending_lba_for_partition} ( Sector )")
        print("    ( ... )")
        print(f"[ + ] Number of Partition Entries : {number_of_partition_entries}")
        print(f"[ + ] Size of Partition Entry : {size_of_partition_entry} ( Byte )")
        print("    ( ... )")

        return partition_table_entry_starting_lba, number_of_partition_entries, size_of_partition_entry

    """
    GPT - Partition Entries
    """
    def get_gpt_partition_entries(self, f) :
        partition_table_entry_starting_lba, number_of_partition_entries, size_of_partition_entry = self.get_gpt_header(f)

        partition_table_offset = partition_table_entry_starting_lba * SECTOR_SIZE
        f.seek(partition_table_offset)

        partiton_table_entries_data = f.read(size_of_partition_entry * number_of_partition_entries)

        for index in range(number_of_partition_entries) :
            partition_table_entry_data = partiton_table_entries_data[index * size_of_partition_entry : (index + 1) * size_of_partition_entry]
        
            partition_table_entry_fields = struct.unpack("<16s16sQQQ72s", partition_table_entry_data)

            partition_type_guid = partition_table_entry_fields[0]
            unique_partition_guid = partition_table_entry_fields[1]
            first_lba = partition_table_entry_fields[2]
            last_lba = partition_table_entry_fields[3]
            attribute_flags = partition_table_entry_fields[4].to_bytes(8, byteorder='little')
            partition_name = partition_table_entry_fields[5].decode(errors='ignore')
            partition_size = (last_lba - first_lba + 1) * SECTOR_SIZE / (1024 * 1024)

            if first_lba > 0 :
                print(f"\n@GPT - Partition Entry - #{index}")
                print(f"[ + ] Partition Type GUID : {self.print_hex(int.from_bytes(partition_type_guid, byteorder='little'))}")
                print(f"[ + ] Unique Partition GUID : {self.print_hex(int.from_bytes(unique_partition_guid, byteorder='little'))}")
                print(f"[ + ] First LBA : {first_lba} ( Sector )")
                print(f"[ + ] Last LBA : {last_lba} ( Sector )")
                print(f"[ + ] Attribute Flags : {" ".join(f"{byte:02X}" for byte in (attribute_flags))}")
                print(f"[ + ] Partition Name : {partition_name}")
                print(f"[ + ] Partition Size : {partition_size} ( MB )")

                self.partition_list.append({
                    "Index" : index,
                    "Partition Type GUID" : partition_type_guid,
                    "Unique Partition GUID" : unique_partition_guid,
                    "First LBA" : first_lba,
                    "Last LBA" : last_lba,
                    "Attribute Flags" : attribute_flags,
                    "Partition Name" : partition_name,
                    "Partition Size" : partition_size
                })
        
        print(f"\n@GPT - Partition Entries")
        # print(f"Partitions : {partition_list}")
        print(f">>>> Total Number of Partitions : {len(self.partition_list)}")

    """
    GPT
    """
    def get_gpt(self, f) :
        print("\n# GPT")

        print("\n========================================")

        # [ 1 ] Protective MBR
        self.get_protective_mbr(f)

        # [ 2 ] ( Primary ) GPT Header + Partition Entries
        self.get_gpt_partition_entries(f)

        print("\n========================================")
    
    """
    NTFS - VBR
    """
    def get_vbr(self, f, partition) :
        partition_first_offset = partition.get("First LBA")
        partition_last_offset = partition.get("Last LBA")

        f.seek(partition_first_offset * SECTOR_SIZE)

        vbr_data = f.read(SECTOR_SIZE)

        jump_boot_code = vbr_data[0:3]
        oem_id = vbr_data[3:11]
        bpb_data = vbr_data[11:84]
        boot_code = vbr_data[84:510]
        vbr_signature = vbr_data[510:512]

        # NTFS
        if oem_id != NTFS_OEM_ID :
            return False
        

        if vbr_signature != VBR_SIGNATURE :
            print("\n[ ERROR ] FAIL - VBR Signature ( 55 AA )")
            print(f">>>>>>>>>> File Path : {self.file_path}")
            print(f"{vbr_signature}")
            sys.exit(1)
        
        print("\n# Partition : NTFS - VBR")

        bpb_fields = struct.unpack("<HBH5sB18sQQQB3sB3sQI", bpb_data)
        
        bytes_per_sector = bpb_fields[0]
        sectors_per_cluster = bpb_fields[1]
        reserved_sector_count = bpb_fields[2]
        reserved_1 = bpb_fields[3]
        media_type = bpb_fields[4]
        reserved_2 = bpb_fields[5]
        total_sectors = bpb_fields[6]
        start_cluster_for_mft = bpb_fields[7]
        start_cluster_for_mftmirr = bpb_fields[8]
        cluster_per_entry = bpb_fields[9]
        reserved_3 = bpb_fields[10]
        cluster_per_index = bpb_fields[11]
        reserved_4 = bpb_fields[12]
        volume_serial_number = bpb_fields[13]
        reserved_5 = bpb_fields[14]

        print(f"[ + ] Jump Boot Code : {" ".join(f"{byte:02X}" for byte in jump_boot_code)}")
        print(f"[ + ] OEM ID ( STR / HEX ) : {oem_id.decode(errors='errors').strip()} / {" ".join(f"{byte:02X}" for byte in oem_id)}")
        print(f"[ + ] Bytes Per Sector : {bytes_per_sector} ( Byte )")
        print(f"[ + ] Sectors Per Cluster : {sectors_per_cluster} ( Sector )")
        print(f"    ( ... )")
        print(f"[ + ] Start Cluster for $MFT : {start_cluster_for_mft} ( Sector )")
        print(f"[ + ] Start Cluster for $MFTMirr : {start_cluster_for_mftmirr} ( Sector )")
        print(f"    ( ... )")

        self.bytes_per_sector = bytes_per_sector
        self.sectors_per_cluster = sectors_per_cluster

        self.partition_start_sector = partition_first_offset
        self.partition_start_offset = self.partition_start_sector * self.bytes_per_sector
        self.mft_start_sector = partition_first_offset + start_cluster_for_mft * self.sectors_per_cluster
        self.mft_start_offset = self.mft_start_sector * self.bytes_per_sector

        return True

    """
    NTFS - MFT Entries - $MFT
    """
    def get_mft_entries_count(self, f) :
        f.seek(self.mft_start_offset)

        mft_entry_size = 1024

        mft_data = f.read(mft_entry_size)

        # MFT Entry Header - $MFT
        mft_entry_header_data = mft_data[0:48]

        mft_entry_header_signature = mft_entry_header_data[0:4]
        offset_of_fixup_array = mft_entry_header_data[4:6]
        entries_in_fixup_array = mft_entry_header_data[6:8]
        log_file_sequence_number = mft_entry_header_data[8:16]
        sequence_number = mft_entry_header_data[16:18]
        hard_link_count = mft_entry_header_data[18:20]
        offset_of_file_attribute = mft_entry_header_data[20:22]
        flags = mft_entry_header_data[22:24]
        real_size_of_mft_entry = mft_entry_header_data[24:28]
        allocated_size_of_mft_entry = mft_entry_header_data[28:32]
        file_reference_to_base_entry = mft_entry_header_data[32:40]
        next_attribute_id = mft_entry_header_data[40:42]
        allign_to_4b_boundary = mft_entry_header_data[42:44]
        number_of_this_mft_entry = mft_entry_header_data[44:48]

        if mft_entry_header_signature != MFT_ENTRY_HEADER_SIGNATURE :
            print("\n[ ERROR ] FAIL - MFT Entry Header Signature ( FILE )")
            print(f">>>>>>>>>> File Path : {self.file_path}")
            print(f"{mft_entry_header_signature.decode(errors='ignore')}")
            sys.exit(1)
        
        # MFT Entry Header - $MFT - Attribute Header
        attribute_offset = int.from_bytes(offset_of_file_attribute, byteorder='little')

        while attribute_offset < mft_entry_size :
            # print(f"[ DEBUG ] Attribute Offset : {attribute_offset}")

            attribute_header_data = mft_data[attribute_offset:attribute_offset+16]

            attribute_type_id = int.from_bytes(attribute_header_data[0:4], byteorder='little')
            length_of_attribute = attribute_header_data[4:8]
            non_resident_flag = attribute_header_data[8:9]
            length_of_name = attribute_header_data[9:10]
            offset_to_name = attribute_header_data[10:12]
            flags = attribute_header_data[12:14]
            attribute_identifier = attribute_header_data[14:16]

            # End
            if attribute_type_id == 0xFFFFFFFF :
                break

            # $DATA
            if attribute_type_id == 0x80 :
                non_resident_flag = mft_data[attribute_offset+0x08:attribute_offset+0x08+1]

                # Resident
                if non_resident_flag == 0 :
                    mft_size = int.from_bytes(mft_data[attribute_offset+0x10:attribute_offset+0x10+4], byteorder='little') # Resident - Size of $MFT
                
                # Non-Resident
                else :
                    mft_size = int.from_bytes(mft_data[attribute_offset+0x30:attribute_offset+0x30+8], byteorder='little') # Non-Resident - Size of $MFT
            
                mft_entries_count = mft_size // mft_entry_size

                return mft_entries_count
            
            # print(f"[ DEBUG ] Length of Attribute : {length_of_attribute}")
            
            attribute_offset += int.from_bytes(length_of_attribute, byteorder='little')
        
        return 0

    """
    NTFS - MFT Entries - MFT Entry
    """
    def get_mft_entry(self, f) :
        print()
    
    """
    NTFS - MFT Entries
    """
    def get_mft_entries(self, f) :
        print("\n# Partition : NTFS - MFT Entries")
        print(f">>>> MFT ( Start ) Sector : {self.mft_start_sector} ( Sector )")

        mft_entry_size = 1024

        mft_entries_count = self.get_mft_entries_count(f)

        print(f">>>> Total Number of MFT Entries : {mft_entries_count}")

        # MFT Entry
        for index in range(mft_entries_count) :
            f.seek(self.mft_start_offset + (mft_entry_size * index))

            mft_entry = f.read(mft_entry_size)

            # End
            if len(mft_entry) < mft_entry_size :
                break

            # MFT Entry - MFT Entry Header
            mft_entry_header_signature = mft_entry[0:4]
            offset_of_fixup_array = mft_entry[4:6]
            entries_in_fixup_array = mft_entry[6:8]
            log_file_sequence_number = mft_entry[8:16]
            sequence_number = mft_entry[16:18]
            hard_link_count = mft_entry[18:20]
            offset_of_file_attribute = mft_entry[20:22]
            mft_entry_flags = mft_entry[22:24]
            real_size_of_mft_entry = mft_entry[24:28]
            allocated_size_of_mft_entry = mft_entry[28:32]
            file_reference_to_base_entry = mft_entry[32:40]
            next_attribute_id = mft_entry[40:42]
            allign_to_4b_boundary = mft_entry[42:44]
            number_of_this_mft_entry = mft_entry[44:48]

            if mft_entry_header_signature != MFT_ENTRY_HEADER_SIGNATURE :
                continue

            is_deleted_file = False

            if (int.from_bytes(mft_entry_flags, byteorder='little') == 0) or (int.from_bytes(allocated_size_of_mft_entry, byteorder='little') == 0) :
                is_deleted_file = True
                
            # MFT Entry - Attribute Header
            attribute_offset = int.from_bytes(offset_of_file_attribute, byteorder='little')

            while attribute_offset < mft_entry_size :
                # print(f"[ DEBUG ] Attribute Offset : {attribute_offset}")

                attribute_header_data = mft_entry[attribute_offset:attribute_offset+16]

                attribute_type_id = int.from_bytes(attribute_header_data[0:4], byteorder='little')
                length_of_attribute = int.from_bytes(attribute_header_data[4:8], byteorder='little')
                non_resident_flag = int.from_bytes(attribute_header_data[8:9], byteorder='little')
                length_of_name = int.from_bytes(attribute_header_data[9:10], byteorder='little')
                offset_to_name = int.from_bytes(attribute_header_data[10:12], byteorder='little')
                attribute_flags = attribute_header_data[12:14]
                attribute_identifier = attribute_header_data[14:16]

                # End
                if attribute_type_id == 0xFFFFFFFF :
                    break

                # $FILE_NAME
                if attribute_type_id == 0x30 :
                                        
                    # MFT Entry - Attribute Header - Resident
                    if non_resident_flag == 0 :
                        # print("[ DEBUG ] Resident")

                        resident_attribute_header_data = mft_entry[attribute_offset+16:attribute_offset+32]

                        length_of_attribute_content = resident_attribute_header_data[0:4]
                        offset_to_attribute_data = int.from_bytes(resident_attribute_header_data[4:6], byteorder='little')
                        indexed_flag = resident_attribute_header_data[6:7]
                        reserved = resident_attribute_header_data[7:8]
                        attribute_name = resident_attribute_header_data[8:16]

                        file_name_length_offset = attribute_offset + offset_to_attribute_data + 0x40
                        file_name_length = int.from_bytes(mft_entry[file_name_length_offset:file_name_length_offset+1], byteorder='little')

                        if file_name_length == 0:
                            attribute_offset += length_of_attribute

                            continue                            

                        file_name_offset = attribute_offset + offset_to_attribute_data + 0x42
                        file_name_bytes = mft_entry[file_name_offset : file_name_offset + (file_name_length * 2)]
                        file_name = file_name_bytes.decode('utf-16-le', errors='ignore').strip("\x00")

                    # MFT Entry - Attribute Header - Non-Resident : [ To - Do ]
                    else :
                        # print("[ DEBUG ] Non-Resident")

                        file_name = ""

                    if is_deleted_file == True :
                        self.file_list.append((file_name, "Deleted"))
                        self.deleted_file_list.append(file_name)
                    else :
                        self.file_list.append((file_name, "Active"))

                attribute_offset += length_of_attribute
        
        file_name_only = [file[0] for file in self.file_list]
        deleted_file_name_only = [file for file in self.deleted_file_list]

        print("\n# Partition : NTFS - File List")
        print(f"{file_name_only}")
        print(f">>>> Total Number of Files : {len(self.file_list)}")

        print("\n# Partition : NTFS - Deleted File List")
        print(f"{deleted_file_name_only}")
        print(f">>>> Total Number of Files : {len(self.deleted_file_list)}")

    """
    NTFS
    """
    def get_ntfs(self, f) :
        print("\n# NTFS")

        is_ntfs = False

        print("\n========================================")

        for index, partition in enumerate(self.partition_list) :
            is_ntfs = self.get_vbr(f, partition)

            if is_ntfs == True :
                self.get_mft_entries(f)
            else :
                continue

        print("\n========================================")
            
    """
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
        print("How to Use : python GPT_NTFS_Parse.py < ( GPT )NTFS File Path >")
        sys.exit(1)
    
    ntfs_file = sys.argv[1]
    parse = NTFSParse(ntfs_file)
    parse.parse()
