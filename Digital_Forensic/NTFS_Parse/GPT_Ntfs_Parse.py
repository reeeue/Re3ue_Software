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

        # NTFS - VBR
        self.bytes_per_sector = 0
        self.sector_per_cluster = 0

        # NTFS - VBR
        self.partition_start_sector = 0
        self.partition_start_offset = 0
        self.mft_start_sector = 0
        self.mft_start_offset = 0

        self.partition_list = []
        self.file_list = []
        self.deleted_file_list = []
        self.file_data_list = []
        self.deleted_file_data_list = []
    
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
                    "Starting LBA" : starting_lba,
                    "Ending LBA" : ending_lba,
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
    NTFS - VBR
    """
    def get_vbr(self, f, partition) :
        partition_starting_offset = partition.get("Starting LBA")
        partition_ending_offset = partition.get("Ending LBA")

        f.seek(partition_starting_offset * SECTOR_SIZE)

        vbr_data = f.read(SECTOR_SIZE)

        jump_boot_code = vbr_data[0:3] # 3 Bytes
        oem_id = vbr_data[3:11] # 8 Bytes
        bpb_data = vbr_data[11:84] # 73 Bytes
        boot_code = vbr_data[84:510] # 426 Bytes
        vbr_signature = vbr_data[510:512] # 2 Bytes

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
        reserved_sectors_count = bpb_fields[2]
        reserved_1 = bpb_fields[3]
        media_type = bpb_fields[4]
        reserved_2 = bpb_fields[5]
        total_sectors = bpb_fields[6]
        start_cluster_for_mft = bpb_fields[7]
        start_cluster_for_mftmirr = bpb_fields[8]
        cluster_per_entry = bpb_fields[9]
        reserved_3 = bpb_fields[10]
        clusters_per_index = bpb_fields[11]
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

        self.partition_start_sector = partition_starting_offset
        self.partition_start_offset = self.partition_start_sector * self.bytes_per_sector
        self.mft_start_sector = partition_starting_offset + start_cluster_for_mft * self.sectors_per_cluster
        self.mft_start_offset = self.mft_start_sector * self.bytes_per_sector

        return True

    """
    NTFS - MFT Entries - MFT Entry - $MFT
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
        mft_entry_number = mft_entry_header_data[44:48]

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

        deleted_file_index = 0
        deleted_file_directory = os.getcwd()

        # MFT Entry
        for index in range(mft_entries_count) :
            deleted_file_flag = False

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
            mft_entry_number = mft_entry[44:48]

            if mft_entry_header_signature != MFT_ENTRY_HEADER_SIGNATURE :
                continue

            # Deleted File #0 - Flag
            mft_entry_flag = int.from_bytes(mft_entry_flags, byteorder='little')
            deleted_file_flag = (mft_entry_flag == 0x0000)

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

                        resident_attribute_header_data = mft_entry[attribute_offset+16:attribute_offset+32] # ( Resident ) Attribute Header : 32 Bytes

                        length_of_attribute_content = resident_attribute_header_data[0:4]
                        offset_to_attribute_data = int.from_bytes(resident_attribute_header_data[4:6], byteorder='little')
                        indexed_flag = resident_attribute_header_data[6:7]
                        reserved = resident_attribute_header_data[7:8]
                        attribute_name = resident_attribute_header_data[8:16]

                        # $FILE_NAME - Attribute Content
                        file_name_length_offset = attribute_offset + offset_to_attribute_data + 0x40
                        file_name_length = int.from_bytes(mft_entry[file_name_length_offset:file_name_length_offset+1], byteorder='little')

                        if file_name_length == 0:
                            attribute_offset += length_of_attribute

                            continue                            

                        file_name_offset = attribute_offset + offset_to_attribute_data + 0x42
                        file_name_bytes = mft_entry[file_name_offset : file_name_offset + (file_name_length * 2)]
                        file_name = file_name_bytes.decode('utf-16-le', errors='ignore').strip("\x00")

                    # MFT Entry - Attribute Header - Non-Resident
                    else :
                        # print("[ DEBUG ] Non-Resident")

                        non_resident_attribute_header_data = mft_entry[attribute_offset+16:attribute_offset+72] # ( Non-Resident ) Attribute Header : 72 Bytes

                        start_vcn_of_run_list = attribute_header_data[0:8]
                        end_vcn_of_run_list = attribute_header_data[8:16]
                        offset_to_run_list = attribute_header_data[16:18]
                        compress_unit_size = attribute_header_data[18:20]
                        reserved = attribute_header_data[20:24]
                        allocated_size_of_attribute_content = attribute_header_data[24:32]
                        real_size_of_attribute_content = attribute_header_data[32:40]
                        initial_size_of_attribute_content = attribute_header_data[40:48]
                        attribute_name = attribute_header_data[48:56]

                        # $FILE_NAME - Attribute Content => [ To - Do ]
                        file_name_length_offset = 0
                        file_name_length = 0

                        if file_name_length == 0:
                            attribute_offset += length_of_attribute

                            continue  

                        file_name_offset = 0
                        file_name_bytes = 0
                        file_name = ""

                    self.file_list.append(file_name)

                    # Deleted File #1 - File Name
                    if deleted_file_flag == True :
                        self.deleted_file_list.append(file_name)

                    attribute_offset += length_of_attribute

                    continue

                # $DATA
                if attribute_type_id == 0x80 :

                    # MFT Entry - Attribute Header - Resident
                    if non_resident_flag == 0 :
                        # print("[ DEBUG ] $DATA : Resident")

                        resident_attribute_header_data = mft_entry[attribute_offset+16:attribute_offset+32] # ( Resident ) Attribute Header : 32 Bytes

                        length_of_attribute_content = resident_attribute_header_data[0:4]
                        offset_to_attribute_data = int.from_bytes(resident_attribute_header_data[4:6], byteorder='little')
                        indexed_flag = resident_attribute_header_data[6:7]
                        reserved = resident_attribute_header_data[7:8]
                        attribute_name = resident_attribute_header_data[8:16]

                        # $DATA - Attribute Content
                        file_data_length = int.from_bytes(length_of_attribute_content, byteorder='little')
                        file_data_offset = attribute_offset + offset_to_attribute_data

                        if file_data_length == 0:
                            attribute_offset += length_of_attribute

                            continue  

                        file_data = mft_entry[file_data_offset:file_data_offset+file_data_length]

                    # MFT Entry - Attribute Header - Non-Resident
                    else :
                        # print("[ DEBUG ] $DATA : Non-Resident")

                        non_resident_attribute_header_data = mft_entry[attribute_offset+16:attribute_offset+72] # ( Non-Resident ) Attribute Header : 72 Bytes

                        start_vcn_of_run_list = attribute_header_data[0:8]
                        end_vcn_of_run_list = attribute_header_data[8:16]
                        offset_to_run_list = attribute_header_data[16:18]
                        compress_unit_size = attribute_header_data[18:20]
                        reserved = attribute_header_data[20:24]
                        allocated_size_of_attribute_content = attribute_header_data[24:32]
                        real_size_of_attribute_content = attribute_header_data[32:40]
                        initial_size_of_attribute_content = attribute_header_data[40:48]
                        attribute_name = attribute_header_data[48:56]

                        # $DATA - Attribute Content => [ To - Do ]
                        file_data_length = 0
                        file_data_offset = 0

                        if file_data_length == 0:
                            attribute_offset += length_of_attribute

                            continue  

                        file_data = 0

                    self.file_data_list.append({file_data})

                    # Deleted File #2 - File Data
                    if deleted_file_flag == True :
                        self.deleted_file_data_list.append(file_data)

                        deleted_file_name = f"deleted_file_{deleted_file_index}"
                        deleted_file_path = os.path.join(deleted_file_directory, deleted_file_name)
                        
                        with open(deleted_file_path, 'wb') as deleted_file :
                            deleted_file.write(file_data)
                        
                        deleted_file_index += 1

                    attribute_offset += length_of_attribute

                    continue

                attribute_offset += length_of_attribute
        
        print("\n# Partition : NTFS - File List")
        print(f"{self.file_list}")
        print(f">>>> Total Number of Files : {len(self.file_list)}")

        print("\n# Partition : NTFS - Deleted File List")
        print(f"{self.deleted_file_list}")
        print(f">>>> Total Number of Deleted Files : {len(self.deleted_file_list)}")
    
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
    NTFS
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
