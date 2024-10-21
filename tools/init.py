import random, os, sys, getpass
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from solders.keypair import Keypair

# 用AES算法，enword作为密钥解密数据
# using AES algorithm with enword as key to decrypt data
def decrypt_data(enword, data):
    cipher = AES.new(pad(enword.encode(), AES.block_size), AES.MODE_ECB)
    return unpad(cipher.decrypt(data), AES.block_size)

# 用AES算法，enword作为密钥加密数据
# using AES algorithm with enword as key to encrypt data
def encrypt_data(enword, data):
    cipher = AES.new(pad(enword.encode(), AES.block_size), AES.MODE_ECB)
    return cipher.encrypt(pad(data, AES.block_size))

# 用AES算法，enword作为密钥解密数字类型的数据
# using AES algorithm with enword as key to decrypt data of number type
def decrypt_data_from_int(enword, private_key_encrypt_for_print_number):
    cipher = AES.new(pad(enword.encode(), AES.block_size), AES.MODE_ECB)
    private_key_encrypt_for_print = private_key_encrypt_for_print_number.to_bytes(96, byteorder='little')
    private_key = unpad(cipher.decrypt(private_key_encrypt_for_print), AES.block_size)
    return private_key

# 用AES算法，enword作为密钥加密数据，并转为数字类型
# using AES algorithm with enword as key to encrypt data and convert to number type
def encrypt_data_to_int(enword, private_key):
    cipher = AES.new(pad(enword.encode(), AES.block_size), AES.MODE_ECB)
    private_key_encrypt_for_print = cipher.encrypt(pad(private_key, AES.block_size))
    private_key_encrypt_for_print_number = int.from_bytes(private_key_encrypt_for_print, byteorder='little')
    return private_key_encrypt_for_print_number

def recover_privatekey(enword=None, secret=None):
    if not secret:
        secret = int(input("secret number:"))
    if not enword:
        enword = input("enword:")
    private_key = decrypt_data_from_int(enword, secret).decode()
    return private_key


def run_init():

    print("1. Initilizing Solana Wallet")
   
    raw_private_key = getpass.getpass("Input your Private Key:")
    sol_address = str(Keypair.from_base58_string(raw_private_key).pubkey())
    print("Your Solana Address(Check carefully):", sol_address)
    
    print("2. Encrypting private key for print!!")
    enword = getpass.getpass("Input your simple password:")
    private_key_encrypt_for_print_number = encrypt_data_to_int(enword, raw_private_key.encode())
    print("Save this number(Will be save to disk):", private_key_encrypt_for_print_number)
    
    # check if the private key can be recovered
    assert recover_privatekey(enword, private_key_encrypt_for_print_number) == raw_private_key
    
    # create a directory to save the encrypted private key
    os.makedirs("sol_" + sol_address, exist_ok=True)
    
    with open("sol_" + sol_address + "/encrypted_private_key.txt", "w") as f:
        f.write(str(private_key_encrypt_for_print_number))
        print(f"Encrypted private key saved to sol_{sol_address}/encrypted_private_key.txt")
    
    binance_address = input("3. Input your Binance deposit address:")
    with open("sol_" + sol_address + "/binance_address.txt", "w") as f:
        f.write(str(binance_address))
    
    print("All Done!")

if __name__ == "__main__":
    run_init()