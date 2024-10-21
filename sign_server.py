
from flask import Flask, request, jsonify, g, session
from orm import database
from tools.init import run_init
from signer.client import Signer
from shield import shield
import sys, getpass, json, datetime
from gevent.pywsgi import WSGIServer

def get_server():
    
    # 初始化密钥获取器
    # init the private key getter
    shield.SHIELD = shield.Shield()
    
    # get database by SOL address
    database.database = database.config_database(shield.SHIELD.address)
        
    from router.sol import sol_bp
    from orm.sol_request import SolRequest
    if not SolRequest.table_exists():
        SolRequest.create_table()
        
    app = Flask(__name__)
    app.register_blueprint(sol_bp, url_prefix='/sol')
    
    app.config["SECRET_KEY"] = shield.SHIELD.auth_password
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=1)
    
    SIGNER = Signer("localhost", shield.SHIELD.auth_password)
    
    @app.route('/login', methods=['POST'])
    def login():
        data = g.data
        password = data["password"]
        if password == shield.SHIELD.auth_password:
            session["pass"] = shield.SHIELD.auth_password
            return "ok"
        return "fail"
    
    @app.before_request
    def before_request_func():
        if database.database.is_closed():
            database.database.connect()
            
        data = request.get_json()
        # 解密通讯过程中的数据
        # decrypt the data during the communication
        data = SIGNER.decrypt(data["data"])
        if data.get("pass") == shield.SHIELD.address: # 校验地址 check the address
            g.data = data
        else:
            return jsonify({"error": "Unauthorized"}), 401

    @app.after_request
    def after_request_func(response):
        jsondata = response.get_json()
        # 加密返回的数据
        # encrypt the returned data
        data = SIGNER.encrypt(jsondata)
        response.set_data(json.dumps({"data": data}))
        
        return response

    return app

if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else "run"
    port = sys.argv[2] if len(sys.argv) > 2 else 80
    print(sys.argv)
    if arg == "init": # 初始化密钥 init the private key
        run_init()
    elif arg == "debug":
        app = get_server()
        app.run(host="0.0.0.0", port=8011, debug=False)
    else:
        app = get_server()
        http_server = WSGIServer(("0.0.0.0", int(port)), app)
        print(f"Server is stated at port {port}, you can now close your shell. Signer is running in tmux.")
        http_server.serve_forever()
    