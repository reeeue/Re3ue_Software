# [ Re3ue ] XOR.py

import os
import sys

class XOR :
    """
    """
    def __init__(self, input_file_path) :
        self.input_file_path = input_file_path
        self.output_file_path = "Output_XOR"
        self.key = None
    
    """
    """
    def encrypt_decrypt(self, f) :
        file_data = f.read()

        key_bytes = self.key.encode()
        key_length = len(self.key)

        result_data = bytearray()

        for i, byte in enumerate(file_data) :
            result_data.append(byte ^ key_bytes[i % key_length])

        return bytes(result_data)
    
    """
    """
    def output_file(self, file_data) :
        try :
            with open(self.output_file_path, "wb") as f :
                f.write(file_data)
        
        except IOError as e :
            print("\n[ ERROR ] FAIL - Write Output File")
            sys.exit(1)
    
    """
    """
    def execute(self) :
        print("Encrypt / Decrypt Start.")

        with open(self.input_file_path, "rb") as f :
            print("\nKEY")
            self.key = input(">>>> ")

            result_data = self.encrypt_decrypt(f)

            self.output_file(result_data)

        print("\nEncrypt / Decrypt End.")

# Main
if __name__ == "__main__" :
    # How to Use
    if len(sys.argv) != 2 :
        print("How to Use : python XOR.py < File Path >")
        sys.exit(1)
    
    input_file_path = sys.argv[1]
    xor = XOR(input_file_path)
    xor.execute()
