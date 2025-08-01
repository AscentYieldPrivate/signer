import time, random, os, sys
import contextlib, getpass
import secrets
import gc
from tools.init import decrypt_data_from_int, encrypt_data_to_int
from solders.keypair import Keypair
    
class Shield:
    
    def __init__(self):
        self.address = None
        count = 0
        for dir in os.listdir("."):
            if dir.startswith("sol_"):
                count += 1
                self.address = dir.removeprefix("sol_")
        
        if count != 1:
            self.address = input("Input your SOL address:")
            if not os.path.exists("sol_" + self.address):
                raise ValueError("Address not found!")
        
        self.encrypted_private_key = ""
        self.binance_address = ""

        # load the encrypted private key
        with open("sol_" + self.address + "/encrypted_private_key.txt", "r") as f:
            self.encrypted_private_key = int(f.readline().strip())
        
        with open("sol_" + self.address + "/binance_address.txt", "r") as f:
            self.binance_address = f.readline().strip()
        
        while True:
            self.simple_password = getpass.getpass("Input your private key password:")
            try:
                with self.get_private_key() as private_key:
                    assert self.address == str(Keypair.from_base58_string(private_key).pubkey())
            except Exception as e:
                print("Password Error! Please input again!")
                continue
            break
        

    @contextlib.contextmanager
    def get_private_key(self):
        private_key = None
        try:
            private_key = decrypt_data_from_int(self.simple_password, self.encrypted_private_key).decode()
            yield private_key
        finally:
            if private_key:
                del private_key
                gc.collect()

    
SHIELD = None