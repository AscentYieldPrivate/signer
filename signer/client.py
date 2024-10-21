import json, base64, getpass, requests, os
from tools.init import decrypt_data, encrypt_data
from shield import shield
from solders.pubkey import Pubkey

class Signer:
    
    def __init__(self, sign_server_ip, auth_password):
        self.sign_server_ip = sign_server_ip
        self.auth_password = auth_password
    
    def sign_sol(self, trans, sign_address, void_keypair, function="", tokenaddress=""):
        session = requests.session()
        session.post(f"http://{self.sign_server_ip}/login",json={
            "data":self.encrypt({
                "pass": sign_address,
                "password": self.auth_password
            })
        })
        
        data = {
            "function": function,
            "transaction" : trans,
            "sign_address": sign_address,
            "void_keypair": void_keypair,
            "tokenaddress": tokenaddress,
            "pass": sign_address
        }
        data = {
            "data": self.encrypt(data)
        }

        res = session.post(f"http://{self.sign_server_ip}/sol/sign",json=data)
        return self.decrypt(res.json()["data"])["signature"]["result"]
    
    def encrypt(self, data):
        key = self.auth_password # use the key to encrypt
        return encrypt_data(key[:10], json.dumps(data).encode()).hex()
    
    def decrypt(self, data):
        key = self.auth_password
        return json.loads(decrypt_data(key[:10], bytes.fromhex(data)).decode())

DEFAULT_SIGHER = Signer("localhost:8088", "qwe")


# 后台服务器会使用这个类来请求签名服务器
# The backend server will use this class to request the signature server
class WalletForSigner:
    
    def __init__(self, address, client=DEFAULT_SIGHER):
        self.address = address
        self.client = client
        
    def sign_sol(self, trans, soladdress, void_keypair=None, function="", tokenaddress = ""):
        """
            trans: Sol Transaction
            soladdress: Solana Address(which private key is used to sign the transaction)
            void_keypair: Sol Keypair, the extra signature needed for some transactions
            function: str, the function name of the transaction
        """
        if void_keypair:
            void_keypair = void_keypair.to_json()
        trans = trans.serialize(False).hex() # serialize the transaction
        s = self.client.sign_sol(trans, str(soladdress), void_keypair, function, tokenaddress)
        s = bytes.fromhex(s) # convert the signature to bytes
        return s
    
    def pubkey(self):
        return Pubkey.from_string(self.address)
