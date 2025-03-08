# [ Re3ue ] Ext4_Parse.py

import os
import sys
import struct
import zlib
import math

JOURNAL_SIGNATURE = b"\xC0\x3B\x39\x98"

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
        self.inode_per_group = 0
        self.block_per_group = 0
        self.journal_inode = 0
        self.super_block_check_sum = 0

        # Super Block ( + )
        self.total_group = 0
        self.inode_table_size_per_group = 0

        # Block Group Descriptors
        self.block_group_descriptors = []
        self.delete_inode_direct_blocks = []

        # Journal
        self.journal_offset = 0

        # Journal - Super Block
        self.journal_block_size = 0
        self.journal_total_block = 0
        self.journal_first_transaction_block = 0
        self.journal_new_first_transaction_block = 0

        # Journal - Super Block ( + )
        self.journal_total_transaction_block = 0
        self.journal_first_transaction_block_offset = 0
        self.journal_new_first_transaction_block_offset = 0

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
    """
    def get_file_data(self, f, offset) :
        f.seek(offset)

        file_data = f.read(self.block_size)

        return file_data
    
    """
    """
    def get_file_data_carve(self, f) :
        print()

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
                self.inode_per_group = field_data
                continue
            if field_name == "s_blocks_per_group" :
                self.block_per_group = field_data
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
        
        self.total_group = math.ceil(self.total_block / self.block_per_group)
        self.inode_table_size_per_group = math.ceil(self.inode_size * self.inode_per_group / self.block_size)

        print()

        print(f"[ + ] Total Inode : {self.total_inode}")
        print(f"[ + ] Total Block : {self.total_block}")
        print(f"[ + ] Free Inode : {self.free_inode}")
        print(f"[ + ] Free Block : {self.free_block}")
        print(f"[ + ] Inode Size : {self.inode_size}")
        print(f"[ + ] Block Size : {self.block_size}")
        print(f"[ + ] Inodes per Group : {self.inode_per_group}")
        print(f"[ + ] Blocks per Group : {self.block_per_group}")
        print(f"[ + ] Journal Inode : {self.journal_inode}")
        print(f"[ + ] Check Sum : {self.super_block_check_sum}")

        print(f"[ + ] Total Group : {self.total_group}")
        print(f"[ + ] Inode Table Size Per Group : {self.inode_table_size_per_group}")

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
    EXT4 - Block Groups
    """
    def get_block_groups(self, f) :
        print("\n@3 EXT4 - Block Groups")

        print("\n========================================")

        block_group_descriptor = []

        for list in self.block_group_descriptors :
            block_group_descriptor = list

            # print(block_group_descriptor)
    
        print("\n========================================")

    """
    """

    """
    EXT4 - Journal ( JBD2 ) - Super Block
    """
    def get_journal_super_block(self, f) :
        print("\n@( N + @ ) EXT4 - Journal - Super Block")

        print("\n========================================")
    
        f.seek(self.journal_offset)
        journal_super_block_data = f.read(1024)

        journal_super_block_format = [
            (0x0, "I", "h_magic"),
            (0x4, "I", "h_blocktype"),
            (0x8, "I", "h_sequence"),
            (0xC, "I", "s_blocksize"),
            (0x10, "I", "s_maxlen"),
            (0x14, "I", "s_first"),
            (0x18, "I", "s_sequence"),
            (0x1C, "I", "s_start"),
            (0x20, "I", "s_errno"),
            (0x24, "I", "s_feature_compat"),
            (0x28, "I", "s_feature_incompat"),
            (0x2C, "I", "s_feature_ro_compat"),
            (0x30, "16s", "s_uuid"),
            (0x40, "I", "s_nr_users"),
            (0x44, "I", "s_dynsuper"),
            (0x48, "I", "s_max_transaction"),
            (0x4C, "I", "s_max_trans_data"),
            (0x50, "B", "s_checksum_type"),
            (0x51, "3s", "s_padding2"),
            (0x54, "168s", "s_padding"),
            (0xFC, "I", "s_checksum"),
            (0x100, "768s", "s_users"),
        ]

        for field_offset, field_format, field_name in journal_super_block_format :
            field_size = struct.calcsize(field_format)
            field_data = struct.unpack_from(">" + field_format, journal_super_block_data, field_offset)[0] # Journal - JBD2 : Big Endian

            # print(f"[ + ] {field_name} : {field_data}")

            if field_name == "s_blocksize" :
                self.journal_block_size = field_data
                continue
            if field_name == "s_maxlen" :
                self.journal_total_block = field_data
                continue
            if field_name == "s_first" :
                self.journal_first_transaction_block = field_data
                continue
            if field_name == "s_start" :
                self.journal_new_first_transaction_block = field_data
                continue
        
        print("\n========================================")
    
    """
    EXT4 - Journal ( JBD2 ) - Transaction
    """
    def get_journal_transaction(self, f) :
        transaction_offset = self.journal_first_transaction_block_offset

        f.seek(transaction_offset)

        # ( 1 ) Transaction - Descriptor Block
        journal_descriptor_block_data = f.read(self.journal_block_size) # 1 Block

        block_tag_array_size = self.journal_block_size - (12 + 4)

        block_tag_size = 8 # [ To Do ]

        block_tag_max_count = block_tag_array_size // block_tag_size
        block_tag_count = 0

        block_tag_list = []

        journal_descriptor_block_format = [
            (0x0, "I", "h_magic"),
            (0x4, "I", "h_blocktype"),
            (0x8, "I", "h_sequence"),
            (0xC, f"{block_tag_array_size}s", "block_tag_array"),
            (0xFFC, "I", "t_checksum"),
        ]

        for field_offset, field_format, field_name in journal_descriptor_block_format :
            field_size = struct.calcsize(field_format)
            field_data = struct.unpack_from(">" + field_format, journal_descriptor_block_data, field_offset)[0] # Journal - JBD2 : Big Endian

            # print(f"[ + ] {field_name} : {field_data}")

            if field_name == "block_tag_array" :
                for index in range(block_tag_max_count) :
                    block_tag = field_data[index * block_tag_size : (index + 1) * block_tag_size]
                    block_tag_int = int.from_bytes(block_tag, byteorder='big') # Journal - JBD2 : Big Endian

                    if block_tag_int != 0 :
                        block_tag_list.append({index : block_tag})

                        block_tag_count += 1
                    
                    continue
            
        print(f"[ DEBUG ] Block Tag List : {block_tag_list}")
        print(f"[ DEBUG ] Block Tag Count : {block_tag_count}")

        # ( 2 ) Transaction - Data Block
        # [ To Do ]

        # ( 3 ) Transaction - Commit Block
        # [ To Do ]
    
    """
    EXT4 - Journal ( JBD2 ) - Transactions
    """
    def get_journal_transactions(self, f) :
        print("\n@( N + @ ) EXT4 - Journal - Transactions")

        print("\n========================================")
        
        self.get_journal_transaction(f)

        print("\n========================================")

    """
    EXT4 - Journal ( JBD2 )
    """
    def get_journal(self, f) :
        # ( ... )

        inode_table_offset = 0x8e000 # [ To Do ]

        journal_inode_table_offset = inode_table_offset + (self.journal_inode - 1) * self.inode_size

        f.seek(journal_inode_table_offset)
        journal_inode = f.read(self.inode_size)

        journal_inode_i_block = journal_inode[40:100]

        journal_inode_direct_blocks = []

        for index in range(15) :
            direct_block_data_before = journal_inode_i_block[index * 4 : (index+1) * 4]
            direct_block_data = int.from_bytes(direct_block_data_before, byteorder='little')
            
            # print(f"[ DEBUG ] Direct Block Data ( Before ) : {direct_block_data_before}")

            if direct_block_data != 0 :
                journal_inode_direct_blocks.append({"db_index" : index})
                journal_inode_direct_blocks.append({"db_data" : direct_block_data})
        
        # print(f"[ DEBUG ] Journal Inode - Direct Blocks : {journal_inode_direct_blocks}")

        for journal_inode_direct_block in journal_inode_direct_blocks :
            if 'db_data' in journal_inode_direct_block :
                direct_block_offset = journal_inode_direct_block['db_data'] * self.block_size
            
                f.seek(direct_block_offset)
                journal_signature = f.read(4)

                if journal_signature == JOURNAL_SIGNATURE :
                    self.journal_offset = direct_block_offset

                    break
        
        # Journal - Super Block
        self.get_journal_super_block(f)

        # print(f"[ DEBUG ] Journal - Block Size : {self.print_hex(self.journal_block_size)}")
        # print(f"[ DEBUG ] Journal - Total Block : {self.print_hex(self.journal_total_block)}")
        # print(f"[ DEBUG ] Journal - Start Transaction Block : {self.print_hex(self.journal_first_transaction_block)}")
        # print(f"[ DEBUG ] Journal - End Transaction Block : {self.journal_new_first_transaction_block}")

        journal_transaction_first = self.journal_first_transaction_block
        journal_transaction_new_first = self.journal_new_first_transaction_block

        if journal_transaction_first == journal_transaction_new_first :
            self.journal_total_transaction_block = 0
        elif journal_transaction_first < journal_transaction_new_first :
            self.journal_total_transaction_block = journal_transaction_new_first - journal_transaction_first
        elif journal_transaction_first > journal_transaction_new_first :
            self.journal_total_transaction_block = (self.journal_total_block - self.journal_first_transaction_block) + (self.journal_new_first_transaction_block)

        # print(f"[ DEBUG ] Journal Total Transaction Block : {self.journal_total_transaction_block}")

        journal_first_transaction_block_offset = (self.journal_offset) + self.journal_block_size * self.journal_first_transaction_block
        journal_new_first_transaction_block_offset = (self.journal_offset) + self.journal_block_size * self.journal_new_first_transaction_block

        self.journal_first_transaction_block_offset = journal_first_transaction_block_offset
        self.journal_new_first_transaction_block_offset = journal_new_first_transaction_block_offset

        # Journal - Transactions
        self.get_journal_transactions(f)
        
    """
    """

    """
    EXT4 - Delete Inode - File Data
    """
    def get_delete_inode_file_data(self, f):
        print("\n@( N + 1 ) EXT4 - Delete Inode - File Data")

        print("\n========================================")

        inode_index = 0
        file_data_list = []

        for delete_inode in self.delete_inode_direct_blocks :
            
            for item in delete_inode :
                if 'i_index' in item :
                    inode_index = int(item['i_index'])
                if 'db_data' in item :
                    direct_block_data = int(item['db_data'])
                    file_data = self.get_file_data(f, direct_block_data)

                    # print(f"[ DEBUG ] ( Type ) File Data : {type(file_data)}")

                    if file_data == '' :
                        file_data_list.append(file_data)

            print(f"\n[ Delete Inode ] Index : {inode_index}")
            
            print(delete_inode)
        
        # print(file_data_list)

        print("\n========================================")

    """
    EXT4 - Delete Inode
    """
    def get_delete_inode(self, f) :
        print("\n@( N ) EXT4 - Delete Inode")

        print("\n========================================")

        delete_inode = []

        inode_format = [
            (0x0, "H", "i_mode"),
            (0x2, "H", "i_uid"),
            (0x4, "I", "i_size_lo"),
            (0x8, "I", "i_atime"),
            (0xC, "I", "i_ctime"),
            (0x10, "I", "i_mtime"),
            (0x14, "I", "i_dtime"),
            (0x18, "H", "i_gid"),
            (0x1A, "H", "i_links_count"),
            (0x1C, "I", "i_blocks_lo"),
            (0x20, "I", "i_flags"),
            (0x24, "I", "i_osd1"),
            (0x28, "60s", "i_block"),
            (0x64, "I", "i_generation"),
            (0x68, "I", "i_file_acl_lo"),
            (0x6C, "I", "i_size_high"),
            (0x70, "I", "i_obso_faddr"),
            (0x74, "12s", "i_osd2"),
            (0x80, "H", "i_extra_isize"),
            (0x82, "H", "i_checksum_hi"),
            (0x84, "I", "i_ctime_extra"),
            (0x88, "I", "i_mtime_extra"),
            (0x8C, "I", "i_atime_extra"),
            (0x90, "I", "i_crtime"),
            (0x94, "I", "i_crtime_extra"),
            (0x98, "I", "i_version_hi"),
            (0x9C, "I", "i_projid"),
        ]

        for list in self.block_group_descriptors :
            inode_table_index = 0
            inode_table_offset = 0

            for item in list :
                if 'bg_index' in item :
                    inode_table_index = int(item['bg_index'])
                if 'bg_inode_table' in item :
                    bg_inode_bitmap_data = int(item['bg_inode_table'])
                    inode_table_offset = bg_inode_bitmap_data * self.block_size

            # print(f"[ DEBUG ] Inode Table Offset : {inode_table_offset}")

            print(f"\n[ Inode Table ] Index : {inode_table_index} / Offset ( Hex ) : {self.print_hex(inode_table_offset)}")

            f.seek(inode_table_offset)

            for index in range(self.inode_per_group) :
                inode_data = f.read(self.inode_size)

                inode = []

                inode.append({"i_index" : f"{index}"})

                for field_offset, field_format, field_name in inode_format :
                    field_size = struct.calcsize(field_format)
                    field_data = struct.unpack_from(field_format, inode_data, field_offset)[0]

                    if field_name == "i_dtime" :
                        inode.append({field_name : field_data})
                        continue
                    if field_name == "i_block" :
                        inode.append({field_name : field_data})
                        continue
                            
                for item in inode :
                    if 'i_dtime' in item :
                        i_dtime_data = int(item['i_dtime'])

                        if i_dtime_data != 0 :
                            print(inode)

                            delete_inode.append(inode)

        print("\n========================================")

        delete_inode_direct_blocks = []

        for inode in delete_inode :
            # print("Delete Inode - \"i_block\"")

            delete_inode_direct_block_entry = []

            for item in inode :
                if 'i_index' in item :
                    delete_inode_index = int(item['i_index'])
                    delete_inode_direct_block_entry.append({"i_index" : f"{delete_inode_index}"})

            i_block_data = 0
            direct_block_data = 0

            for item in inode :
                if 'i_block' in item :
                    i_block_data = item['i_block']
            
            # print(f"[ DEBUG ] i_block : {i_block_data}")
            # print(f"[ DEBUG ] i_block ( Type ) : {type(i_block_data)}")

            for index in range(15) :
                direct_block_data_before = i_block_data[index * 4 : (index+1) * 4]
                direct_block_data = int.from_bytes(direct_block_data_before, byteorder='little')
                
                # print(f"[ DEBUG ] Direct Block Data ( Before ) : {direct_block_data_before}")

                if direct_block_data != 0 :
                    delete_inode_direct_block_entry.append({"db_index" : f"{index}"})
                    delete_inode_direct_block_entry.append({"db_data" : f"{direct_block_data}"})
            
            delete_inode_direct_blocks.append(delete_inode_direct_block_entry)

        # print(delete_inode_direct_blocks)

        self.delete_inode_direct_blocks = delete_inode_direct_blocks

        # [ N + 1 ] Delete Inode - File Data
        self.get_delete_inode_file_data(f)
                            
    """
    """

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
            # [ 3 ] Block Group
            self.get_block_groups(f)

            # ( ... )

            # [ N ] Delete Inode
            # [ N + 1 ] Delete Inode - File Data
            self.get_delete_inode(f)

            # ( ... )

            # [ N + @ ] Journal
            self.get_journal(f)

            # ( ... )

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
