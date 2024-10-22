from orm import database
from tools.init import run_init
from shield import shield
import sys
import time, requests


def loop(server):
    
    # 初始化密钥获取器
    # init the private key getter
    shield.SHIELD = shield.Shield()
    
    # get database by SOL address
    database.database = database.config_database(shield.SHIELD.address)
        
    from router.sol import sign
    from orm.sol_request import SolRequest
    if not SolRequest.table_exists():
        SolRequest.create_table()
        
        
    print(f"Client is started, keep signing trans from {server}, you can now close your shell. Signer is running in tmux.")
    while True:
        time.sleep(5)
        
        try:
            # 请求服务器获取需要签名的数据
            # request the server to get the data needed to be signed
            res = requests.post(f"{server}/get_trans", json={
                "address": shield.SHIELD.address
            }, timeout=10)
        
            if database.database.is_closed():
                database.database.connect()
                    
            data = res.json()
            httpdata = res.json()
            if httpdata.get("pass") != shield.SHIELD.address: # 校验地址 check the address
                continue
            data = httpdata.get("data")
            if data and "id" in data:
                print("Need Sign Data Found!", data.get("id"))
                # 走签名逻辑，校验并签名
                # sign the data and verify it
                res = sign(data)
                print(f"Trans {data.get('id')} signed, sending back to server")
                resp = requests.post(f"{server}/send_trans", json={
                    "address": shield.SHIELD.address,
                    "id": data.get("id"),
                    "data": res
                })
                print("Data sent back to server", resp.json())
        except Exception as e:
            print("Error found!!!", repr(e))


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else "run"
    server = sys.argv[2] if len(sys.argv) > 2 else "https://privateclientendpoint.adpolitan.com"
    print(sys.argv)
    if arg == "init": # 初始化密钥 init the private key
        run_init()
    else:
        loop(server)
    