
from orm.sol_request import SolRequest
from parser.sol_parser import check_transaction, sign_transaction
import json, traceback


def sign(data):

    function = data.get("function")
    transaction = data.get("transaction")
    sign_address = data.get("sign_address")
    void_keypair = data.get("void_keypair")
    tokenaddress = data.get("tokenaddress")
    if not transaction or not sign_address:
        return {"error": "Invalid data"}
    
    req = SolRequest.create(transaction=json.dumps(transaction), sign_address=sign_address, function=function)
    
    try:
        check_res = check_transaction(transaction, function, tokenaddress)
        if "error" in check_res:
            req.status = "check_error"
            req.info = check_res["error"]
            req.save()
            print("Error Found", check_res["error"])
            return check_res

        signature = sign_transaction(transaction, void_keypair, function)
        if "error" in signature:
            req.status = "sign_error"
            req.info = signature["error"]
            req.save()
            print("Error Found", signature["error"])
            return signature

        req.signature = signature["result"]
        req.status = "success"
        req.save()
        return {"signature": signature}
    except:
        req.status = "fatal_error"
        req.info = traceback.format_exc()
        req.save()
        print("Fatal Error", traceback.format_exc())
        return {
            "error": "Fatal Error!" + traceback.format_exc()
        }


