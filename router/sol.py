from flask import Blueprint, request, jsonify, g, session
from orm.sol_request import SolRequest
from parser.sol_parser import check_transaction, sign_transaction
from shield import shield
import json, traceback

sol_bp = Blueprint('sol', __name__)


@sol_bp.route('/sign', methods=['POST'])
def sign():
    data = g.data
    
    if "pass" not in session or session["pass"] != shield.SHIELD.auth_password:
        print("Unauthorized")
        return jsonify({"error": "Unauthorized"}), 401

    function = data.get("function")
    transaction = data.get("transaction")
    sign_address = data.get("sign_address")
    void_keypair = data.get("void_keypair")
    if not transaction or not sign_address:
        return jsonify({"error": "Invalid data"}), 400
    
    req = SolRequest.create(transaction=json.dumps(transaction), sign_address=sign_address, function=function)
    
    try:
        check_res = check_transaction(transaction, function)
        if "error" in check_res:
            req.status = "check_error"
            req.info = check_res["error"]
            req.save()
            print("Error Found", check_res["error"])
            return jsonify(check_res), 400

        signature = sign_transaction(transaction, void_keypair)
        if "error" in signature:
            req.status = "sign_error"
            req.info = signature["error"]
            req.save()
            print("Error Found", signature["error"])
            return jsonify(signature), 400

        req.signature = signature["result"]
        req.status = "success"
        req.save()
        return jsonify({"signature": signature}), 200
    except:
        req.status = "fatal_error"
        req.info = traceback.format_exc()
        req.save()
        print("Fatal Error", traceback.format_exc())
        return jsonify({
            "error": "Fatal Error!" + traceback.format_exc()
        }), 400


