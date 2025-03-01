# [ Re3ue ] Ext4_Parse.py

import os
import sys
import struct
import zlib
import math

class Ext4Parse :
    """
    """
    def __init__(self, file_path) :
        self.file_path = file_path

        # Super Block
        self.total_inode = 0
        self.total_block = 0
        self.free_inode = 0
        self.free_block = 0
        self.inode_size = 0
        self.block_size = 0
        self.inodes_per_group = 0
        self.blocks_per_group = 0
        self.journal_inode = 0
        self.super_block_check_sum = 0

        # Super Block ( + )
        self.total_group = 0

        # Block Group Descriptors
        self.block_group_descriptors = []
    
    """
    """
    def print_hex(self, int) :
        format = "0x" + f"{hex(int)[2:].upper()}"

        return format

    """
    """
    def get_true_check_sum_crc32(self, data) :
        true_check_sum_crc32 = zlib.crc32(data)

        return true_check_sum_crc32

    """
    EXT4 - Super Block
    """
    def get_super_block(self, f) :
        print("\n@1 EXT4 - Super Block")

        print("\n========================================")

        f.seek(0x400)
        super_block_data = f.read(1024)

        super_block_format = [
            (0x0, "I", "s_inodes_count"),
            (0x4, "I", "s_blocks_count_lo"),
            (0x8, "I", "s_r_blocks_count_lo"),
            (0xC, "I", "s_free_blocks_count_lo"),
            (0x10, "I", "s_free_inodes_count"),
            (0x14, "I", "s_first_data_block"),
            (0x18, "I", "s_log_block_size"),
            (0x1C, "I", "s_log_cluster_size"),
            (0x20, "I", "s_blocks_per_group"),
            (0x24, "I", "s_clusters_per_group"),
            (0x28, "I", "s_inodes_per_group"),
            (0x2C, "I", "s_mtime"),
            (0x30, "I", "s_wtime"),
            (0x34, "H", "s_mnt_count"),
            (0x36, "H", "s_max_mnt_count"),
            (0x38, "H", "s_magic"),
            (0x3A, "H", "s_state"),
            (0x3C, "H", "s_errors"),
            (0x3E, "H", "s_minor_rev_level"),
            (0x40, "I", "s_lastcheck"),
            (0x44, "I", "s_checkinterval"),
            (0x48, "I", "s_creator_os"),
            (0x4C, "I", "s_rev_level"),
            (0x50, "H", "s_def_resuid"),
            (0x52, "H", "s_def_resgid"),
            (0x54, "I", "s_first_ino"),
            (0x58, "H", "s_inode_size"),
            (0x5A, "H", "s_block_group_nr"),
            (0x5C, "I", "s_feature_compat"),
            (0x60, "I", "s_feature_incompat"),
            (0x64, "I", "s_feature_ro_compat"),
            (0x68, "16s", "s_uuid"),
            (0x78, "16s", "s_volume_name"),
            (0x88, "64s", "s_last_mounted"),
            (0xC8, "I", "s_algorithm_usage_bitmap"),
            (0xCC, "B", "s_prealloc_blocks"),
            (0xCD, "B", "s_prealloc_dir_blocks"),
            (0xCE, "H", "s_reserved_gdt_blocks"),
            (0xD0, "16s", "s_journal_uuid"),
            (0xE0, "I", "s_journal_inum"),
            (0xE4, "I", "s_journal_dev"),
            (0xE8, "I", "s_last_orphan"),
            (0xEC, "4I", "s_hash_seed"),
            (0xFC, "B", "s_def_hash_version"),
            (0xFD, "B", "s_jnl_backup_type"),
            (0xFE, "H", "s_desc_size"),
            (0x100, "I", "s_default_mount_opts"),
            (0x104, "I", "s_first_meta_bg"),
            (0x108, "I", "s_mkfs_time"),
            (0x10C, "17I", "s_jnl_blocks"),
            (0x150, "I", "s_blocks_count_hi"),
            (0x154, "I", "s_r_blocks_count_hi"),
            (0x158, "I", "s_free_blocks_count_hi"),
            (0x15C, "H", "s_min_extra_isize"),
            (0x15E, "H", "s_want_extra_isize"),
            (0x160, "I", "s_flags"),
            (0x164, "H", "s_raid_stride"),
            (0x166, "H", "s_mmp_interval"),
            (0x168, "Q", "s_mmp_block"),
            (0x170, "I", "s_raid_stripe_width"),
            (0x174, "B", "s_log_groups_per_flex"),
            (0x175, "B", "s_checksum_type"),
            (0x176, "H", "s_reserved_pad"),
            (0x178, "Q", "s_kbytes_written"),
            (0x180, "I", "s_snapshot_inum"),
            (0x184, "I", "s_snapshot_id"),
            (0x188, "Q", "s_snapshot_r_blocks_count"),
            (0x190, "I", "s_snapshot_list"),
            (0x194, "I", "s_error_count"),
            (0x198, "I", "s_first_error_time"),
            (0x19C, "I", "s_first_error_ino"),
            (0x1A0, "Q", "s_first_error_block"),
            (0x1A8, "32s", "s_first_error_func"),
            (0x1C8, "I", "s_first_error_line"),
            (0x1CC, "I", "s_last_error_time"),
            (0x1D0, "I", "s_last_error_ino"),
            (0x1D4, "I", "s_last_error_line"),
            (0x1D8, "Q", "s_last_error_block"),
            (0x1E0, "32s", "s_last_error_func"),
            (0x200, "64s", "s_mount_opts"),
            (0x240, "I", "s_usr_quota_inum"),
            (0x244, "I", "s_grp_quota_inum"),
            (0x248, "I", "s_overhead_blocks"),
            (0x24C, "2I", "s_backup_bgs"),
            (0x254, "I", "s_encrypt_algos"),
            (0x258, "16s", "s_encrypt_pw_salt"),
            (0x268, "I", "s_lpf_ino"),
            (0x26C, "I", "s_prj_quota_inum"),
            (0x270, "I", "s_checksum_seed"),
            (0x274, "392s", "s_reserved"),
            (0x3FC, "I", "s_checksum"),
        ]

        for field_offset, field_format, field_name in super_block_format :
            field_size = struct.calcsize(field_format)
            field_data = struct.unpack_from(field_format, super_block_data, field_offset)[0]

            # print(f"[ + ] {field_name} : {field_data}")

            if field_name == "s_inodes_count" :
                self.total_inode = field_data
                continue
            if field_name == "s_blocks_count_lo" :
                self.total_block = field_data
                continue
            if field_name == "s_free_inodes_count" :
                self.free_inode = field_data
                continue
            if field_name == "s_free_blocks_count_lo" :
                self.free_block = field_data
                continue
            if field_name == "s_inodes_per_group" :
                self.inodes_per_group = field_data
                continue
            if field_name == "s_blocks_per_group" :
                self.blocks_per_group = field_data
                continue
            if field_name == "s_inode_size" :
                self.inode_size = field_data
                continue
            if field_name == "s_log_block_size" :
                self.block_size = 2 ** (10 + field_data)
                continue
            if field_name == "s_journal_inum" :
                self.journal_inode = field_data
                continue
            if field_name == "s_checksum" :
                self.super_block_check_sum = field_data
                continue
        
        """
        true_super_block_check_sum = self.get_true_check_sum_crc32(super_block_data)
        if true_super_block_check_sum != self.super_block_check_sum :
            print("\n[ ERROR ] FAIL - CRC ( Integrity )")
            print(f">>>>>>>>>> True Check Sum ( CRC 32 ) : {true_super_block_check_sum}")
            print(f">>>>>>>>>> Field Check Sum ( CRC 32 ) : {self.super_block_check_sum}")
            sys.exit(1)
        """
        
        self.total_group = math.ceil(self.total_block / self.blocks_per_group)

        print(f"[ + ] Total Inode : {self.total_inode}")
        print(f"[ + ] Total Block : {self.total_block}")
        print(f"[ + ] Free Inode : {self.free_inode}")
        print(f"[ + ] Free Block : {self.free_block}")
        print(f"[ + ] Inode Size : {self.inode_size}")
        print(f"[ + ] Block Size : {self.block_size}")
        print(f"[ + ] Inodes per Group : {self.inodes_per_group}")
        print(f"[ + ] Blocks per Group : {self.blocks_per_group}")
        print(f"[ + ] Journal Inode : {self.journal_inode}")
        print(f"[ + ] Check Sum : {self.super_block_check_sum}")

        print(f"[ + ] Total Group : {self.total_group}")

        print("\n========================================")
    
    """
    EXT4 - Block Group Descriptors - Block Group Descriptor
    """
    def get_block_group_descriptor(self, index, input_data) :
        block_group_descriptor = []
        temp = []

        block_group_descriptor_format = [
            (0x00, "I", "bg_block_bitmap_lo"),
            (0x04, "I", "bg_inode_bitmap_lo"),
            (0x08, "I", "bg_inode_table_lo"),
            (0x0C, "H", "bg_free_blocks_count_lo"),
            (0x0E, "H", "bg_free_inodes_count_lo"),
            (0x10, "H", "bg_used_dirs_count_lo"),
            (0x12, "H", "bg_flags"),
            (0x14, "I", "bg_exclude_bitmap_lo"),
            (0x18, "H", "bg_block_bitmap_csum_lo"),
            (0x1A, "H", "bg_inode_bitmap_csum_lo"),
            (0x1C, "H", "bg_itable_unused_lo"),
            (0x1E, "H", "bg_checksum"),
            # 64 Bit Fields ( s_desc_size > 32 ) 
            (0x20, "I", "bg_block_bitmap_hi"),
            (0x24, "I", "bg_inode_bitmap_hi"),
            (0x28, "I", "bg_inode_table_hi"),
            (0x2C, "H", "bg_free_blocks_count_hi"),
            (0x2E, "H", "bg_free_inodes_count_hi"),
            (0x30, "H", "bg_used_dirs_count_hi"),
            (0x32, "H", "bg_itable_unused_hi"),
            (0x34, "I", "bg_exclude_bitmap_hi"),
            (0x38, "H", "bg_block_bitmap_csum_hi"),
            (0x3A, "H", "bg_inode_bitmap_csum_hi"),
            (0x3C, "I", "bg_reserved"),
        ]

        block_group_descriptor.append({"bg_index" : f"{index}"})

        for field_offset, field_format, field_name in block_group_descriptor_format :
            field_size = struct.calcsize(field_format)
            field_data = struct.unpack_from(field_format, input_data, field_offset)[0]
            bit_data_before = bin(field_data)[2:].zfill(16)
            bit_data_after = int(bit_data_before, 2)

            # print(f"[ + ] {field_name} : {field_data}")

            if field_name == "bg_flags" :
                block_group_descriptor.append({f"{field_name}" : f"{field_data}"})
                continue
            if field_name == "bg_checksum" :
                block_group_descriptor.append({f"{field_name}" : f"{field_data}"})
                continue

            # Low : Lower 16 Bits
            if field_name == "bg_block_bitmap_lo" :
                temp.append(bit_data_after) # temp Index : 0
                continue
            if field_name == "bg_inode_bitmap_lo" :
                temp.append(bit_data_after) # temp Index : 1
                continue
            if field_name == "bg_inode_table_lo" :
                temp.append(bit_data_after) # temp Index : 2
                continue
            if field_name == "bg_free_blocks_count_lo" :
                temp.append(bit_data_after) # temp Index : 3
                continue
            if field_name == "bg_free_inodes_count_lo" :
                temp.append(bit_data_after) # temp Index : 4
                continue
            if field_name == "bg_used_dirs_count_lo" :
                temp.append(bit_data_after) # temp Index : 5
                continue
            # High : Upper 16 Bits
            if field_name == "bg_block_bitmap_hi" :
                temp.append(bit_data_after) # temp Index : 6
                continue
            if field_name == "bg_inode_bitmap_hi" :
                temp.append(bit_data_after) # temp Index : 7
                continue
            if field_name == "bg_inode_table_hi" :
                temp.append(bit_data_after) # temp Index : 8
                continue
            if field_name == "bg_free_blocks_count_hi" :
                temp.append(bit_data_after) # temp Index : 9
                continue
            if field_name == "bg_free_inodes_count_hi" :
                temp.append(bit_data_after) # temp Index : 10
                continue
            if field_name == "bg_used_dirs_count_hi" :
                temp.append(bit_data_after) # temp Index : 11
                continue
        
        for temp_index in range(len(temp) // 2) :
            # Low : temp[temp_index]
            # High : temp[temp_index + (len(temp) // 2)]
            full_value = (temp[temp_index + (len(temp) // 2)] << 16) | temp[temp_index]

            if temp_index == 0 :
                block_group_descriptor.append({"bg_block_bitmap" : f"{full_value}"})
                continue
            if temp_index == 1 :
                block_group_descriptor.append({"bg_inode_bitmap" : f"{full_value}"})
                continue
            if temp_index == 2 :
                block_group_descriptor.append({"bg_inode_table" : f"{full_value}"})
                continue
            if temp_index == 3 :
                block_group_descriptor.append({"bg_free_blocks_count" : f"{full_value}"})
                continue
            if temp_index == 4 :
                block_group_descriptor.append({"bg_free_inodes_count" : f"{full_value}"})
                continue
            if temp_index == 5 :
                block_group_descriptor.append({"bg_used_dirs_count" : f"{full_value}"})
                continue

        return block_group_descriptor

    """
    EXT4 - Block Group Descriptors
    """
    def get_block_group_descriptors(self, f) :
        print("\n@2 EXT4 - Block Group Descriptors")

        print("\n========================================")

        block_group_descriptor = []

        f.seek(0x1000)

        for index in range(self.total_group) :
            print(f"\nBlock Group Descriptor #{index}")

            data = f.read(64)

            block_group_descriptor = self.get_block_group_descriptor(index, data)

            for element in block_group_descriptor :
                for key, value in element.items() :
                    print(f"[ + ] {key} : {value}")

            self.block_group_descriptors.append(block_group_descriptor)
        
        print("\n========================================")

    """
    EXT4
    """
    def parse(self) :
        print("Program Start.")

        with open(self.file_path, "rb") as f :
            # [ 1 ] Super Block 
            self.get_super_block(f)
            # [ 2 ] Block Group Descriptors
            self.get_block_group_descriptors(f)

        print("\nProgram End.")

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python Ext4_Parse.py < EXT4 File Path >")
        sys.exit(1)
    
    ext4_file = sys.argv[1]
    parse = Ext4Parse(ext4_file)
    parse.parse()
