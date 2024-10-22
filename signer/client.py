
from solana.transaction import Transaction
from solders.pubkey import Pubkey
from flask import Flask, request, jsonify, g, session
from gevent.pywsgi import WSGIServer
import threading, time, uuid
from log import info_logger, error_logger # 自行编写logger # self-written logger

class TransactionServer:
    
    def __init__(self):
        self.app = self.get_app()
        
        self.pending_trans = {} # 未签名的交易 # unsigned transactions
        self.signed_trans = {} # 已签名的交易 # signed transactions
        self.raw_trans = {} # 未签名的交易数据 # unsigned transaction data
        
        self.trans_lock = threading.Lock()
        
        self.run_thread = threading.Thread(target=self.run)
        self.run_thread.daemon = True
        self.run_thread.start()
        
    
    def get_app(self):
        
        app = Flask(__name__)
        
        # 获取未签名的交易
        # get unsigned transactions
        @app.route('/get_trans', methods=['POST'])
        def get_trans():
            data = request.get_json()
            if "address" not in data:
                error_logger.error("Invalid address! Someone is trying to get transaction without address! "+str(data))
                return {
                    "error": "Invalid address"
                }
            address = data["address"]
            with self.trans_lock:
                if address in self.pending_trans:
                    if len(self.pending_trans[address]) > 0:
                        trans = self.pending_trans[address].pop(0)
                        info_logger.info("Transaction sended for address " + address)
                        return {
                            "pass": address,
                            "data": trans
                        }
                    
            return {
                "pass": address,
                "data": None
            }

        # 获取已签名的交易
        # get signed transactions
        @app.route('/send_trans', methods=['POST'])
        def send_trans():
            data = request.get_json()
            if "address" not in data or "data" not in data or "id" not in data:
                error_logger.error("Invalid address or data! Someone is trying to send transaction without address or data! "+str(data))
                return {
                    "error": "Invalid address or data"
                }
            address = data.get("address")
            id = data.get("id")
            data = data.get("data")
            
            with self.trans_lock:
                if address not in self.signed_trans:
                    self.signed_trans[address] = {}
                self.signed_trans[address][id] = data # 保存已签名的交易 # save signed transactions
                info_logger.info("Transaction signed for address " + address, self.signed_trans)
                    
            return {"status": "ok"}

        return app
    
    def run(self):
        self.http_server = WSGIServer(("0.0.0.0", int(8574)), self.app, log=None)
        info_logger.info("Sign Server is stated at port 8574!")
        self.http_server.serve_forever()
    
    def sign_sol(self, trans, sign_address, void_keypair, function="", tokenaddress=""):
        
        data = {
            "id": uuid.uuid4().hex,
            "function": function,
            "transaction" : trans,
            "sign_address": sign_address,
            "void_keypair": void_keypair,
            "tokenaddress": tokenaddress,
        }
        self.raw_trans[data["id"]] = data

        if sign_address not in self.pending_trans:
            self.pending_trans[sign_address] = []
        self.pending_trans[sign_address].append(data)
        
        waittime = 0
        # 轮训等待签名
        # polling to wait for the signature
        while True:
            time.sleep(0.5)
            waittime += 0.5
            if waittime > 60:
                error_logger.error("Transaction timeout! Retry!"+str(data["id"]))
                raise Exception("Transaction timeout! Check signer server!")
                
            with self.trans_lock:
                if sign_address in self.signed_trans:
                    if data["id"] in self.signed_trans[sign_address]:
                        res = self.signed_trans[sign_address].pop(data["id"])
                        
                        if "error" in res:
                            error_logger.error("Error found in transaction! "+str(res))
                        else:
                            signed_tx = res["signature"]["result"]
                            # 校验签名是否成功
                            # check if the signature is successful
                            signed_tx = Transaction.deserialize(bytes.fromhex(signed_tx))
                            # 提取签名和消息数据
                            # extract the signature and message data
                            signature = signed_tx.signatures[0]
                            message = signed_tx.serialize_message()
                            # 验证签名是否匹配给定的公钥
                            # verify if the signature matches the given public key
                            ok = signature.verify(Pubkey.from_string(sign_address), bytes(message))
                            if ok:
                                self.raw_trans.pop(data["id"])
                                return res["signature"]["result"]

                        error_logger.error("Signature verification failed!!!")
                        self.pending_trans[sign_address].append(self.raw_trans[data["id"]])

transactionServer = TransactionServer()

# 后台服务器会使用这个类来请求签名服务器
# The backend server will use this class to request the signature server
class WalletForSigner:
    
    def __init__(self, address):
        self.address = address

        
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
        s = transactionServer.sign_sol(trans, str(soladdress), void_keypair, function, tokenaddress)
        s = bytes.fromhex(s) # convert the signature to bytes
        return s
    
    def pubkey(self):
        return Pubkey.from_string(self.address)
    