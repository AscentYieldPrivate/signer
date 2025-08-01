from shield.shield import SHIELD
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.transaction import Transaction
from solders.transaction import VersionedTransaction
from solders import message

USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v") # USDC Token address
JLP_MINT = Pubkey.from_string("27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4") # JLP Token address

TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL") # use for token account


# 获取某个钱包的某个token的地址
# Get the sol token account of a token for a wallet
def get_associated_token_address(wallet: Pubkey, mint: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [bytes(wallet), bytes(TOKEN_PROGRAM_ID), bytes(mint)],
        ASSOCIATED_TOKEN_PROGRAM_ID
    )[0]


def check_transaction(transaction, function, tokenaddress=""):
    
    # 只允许两种交易
    # Only two types of transactions are allowed
    if function not in ["jlp_mint_or_burn_sign", "transfer", "jlp_loan_deposit_sign_init",
                        "jlp_loan_deposit_sign", "jlp_loan_borrow_sign",
                        "jlp_loan_repay_sign", "jlp_loan_withdraw_sign"
    ]:
        return {
            "error": "Invalid function"
        }
        
    if function == "jlp_loan_deposit_sign_init":
        t = VersionedTransaction.from_json(transaction)
    else:
        t = Transaction.deserialize(bytes.fromhex(transaction))
    
    # 校验JLP mint的transation是否正确
    # Check if the JLP mint transaction is correct
    if function == "jlp_mint_or_burn_sign":
        if len(t.instructions) != 3:
            return {
                "error": "Invalid jlp_mint_or_burn_sign instructions len"
            }
        
        # 校验是否是mint或burn
        # check if it is mint or burn
        if not t.instructions[2].data.hex().startswith("e4a24e1c46db7473") and not t.instructions[2].data.hex().startswith("e6d7527ff165e392"):
            return {
                "error": "Invalid jlp_mint_or_burn_sign"
            }
        
        # 校验program_id
        # check program_id
        if str(t.instructions[2].program_id) != "PERPHjGBqRHArX4DySjwM6UJHiR3sWAatqfdBS2qQJu" or \
              str(t.instructions[0].program_id) != "ComputeBudget111111111111111111111111111111" or \
                str(t.instructions[1].program_id) != "ComputeBudget111111111111111111111111111111":
            return {
                "error": "Invalid jlp_mint_or_burn_sign program_id"
            }
    
    if function == "transfer":
        if len(t.instructions) != 1:
            return {
                "error": "Invalid transfer instructions len"
            }
        if str(t.instructions[0].program_id) != str(TOKEN_PROGRAM_ID):
            return {
                "error": "Invalid transfer program_id"
            }
    
    # 验证jlp_mint_or_burn_sign的目标地址
    # Verify the target address of jlp_mint_or_burn_sign
    if function == "jlp_mint_or_burn_sign":
        if str(t.instructions[2].accounts[1].pubkey) != str(get_associated_token_address(Pubkey.from_string(SHIELD.address), USDC_MINT)):
            return {
                "error": "Invalid jlp_mint_or_burn_sign address pubkey"
            }
        if str(t.instructions[2].accounts[2].pubkey) != str(get_associated_token_address(Pubkey.from_string(SHIELD.address), JLP_MINT)):
            return {
                "error": "Invalid jlp_mint_or_burn_sign address pubkey"
            }
    
    # 验证transfer的目标地址
    # Verify the target address of transfer
    
    # get token address
    if tokenaddress:
        tokenaddress = Pubkey.from_string(tokenaddress)
    else:
        tokenaddress = USDC_MINT # default
        
    if function == "transfer":
        if str(t.instructions[0].accounts[0].pubkey) != str(get_associated_token_address(Pubkey.from_string(SHIELD.address), tokenaddress)):
            return {
                "error": "Invalid transfer from token address"
            }
        if str(t.instructions[0].accounts[1].pubkey) != str(get_associated_token_address(Pubkey.from_string(SHIELD.binance_address), tokenaddress)):
            return {
                "error": "Invalid transfer to token address"
            }
        if str(t.instructions[0].accounts[2].pubkey) != str(Pubkey.from_string(SHIELD.address)):
            return {
                "error": "Invalid owner address"
            }
        if str(t.instructions[0].accounts[3].pubkey) != str(Pubkey.from_string(SHIELD.address)):
            return {
                "error": "Invalid signer address"
            }
                 
    # 校验JLP loan的transation是否正确
    if function in ["jlp_loan_deposit_sign", "jlp_loan_borrow_sign", "jlp_loan_repay_sign", "jlp_loan_withdraw_sign"]:
        if len(t.instructions) != 3:
            return {
                "error": "Invalid jlp_loan_sign instructions len"
            }
        
        # 校验是否是mint或burn
        # check if it is mint or burn
        if not t.instructions[2].data.hex().startswith("1102c3be4c10ee4a") and not t.instructions[2].data.hex().startswith("99b741417121f92d") \
            and not t.instructions[2].data.hex().startswith("d3dbb7def84a051a") and not t.instructions[2].data.hex().startswith("75a03c52ede92eb6"):
            return {
                "error": "Invalid jlp_loan_sign"
            }
        
        # 校验program_id
        # check program_id
        if str(t.instructions[2].program_id) != "PERPHjGBqRHArX4DySjwM6UJHiR3sWAatqfdBS2qQJu" or \
              str(t.instructions[0].program_id) != "ComputeBudget111111111111111111111111111111" or \
                str(t.instructions[1].program_id) != "ComputeBudget111111111111111111111111111111":
            return {
                "error": "Invalid jlp_loan_sign program_id"
            }
    
    if function == "jlp_loan_deposit_sign_init":
        if len(t.message.instructions) != 3:
            return {
                "error": "Invalid jlp_loan_deposit_sign_init instructions len"
            }
        account_keys = t.message.account_keys
        program_id1 = account_keys[t.message.instructions[0].program_id_index]
        program_id2 = account_keys[t.message.instructions[1].program_id_index]
        program_id3 = account_keys[t.message.instructions[2].program_id_index]
        if str(program_id1) != "ComputeBudget111111111111111111111111111111" or str(program_id2) != "ComputeBudget111111111111111111111111111111" or str(program_id3) != "PERPHjGBqRHArX4DySjwM6UJHiR3sWAatqfdBS2qQJu":
            return {
                "error": "Invalid jlp_loan_deposit_sign_init program_id"
            }
        
        if not t.message.instructions[-1].data.hex().startswith("1102c3be4c10ee4a"):
            return {
                "error": "Invalid jlp_loan_deposit_sign_init data"
            }
            
            
    return {
        "status": "ok"
    }


def sign_transaction(transaction, void_keypair, function):
    with SHIELD.get_private_key() as pk:
        if not pk:
            return {
                "error": "Address not found"
            }
    
        wallet_keypair = Keypair.from_base58_string(pk)
        
        if function == "jlp_loan_deposit_sign_init":
            raw_transaction = VersionedTransaction.from_json(transaction)
            signature = wallet_keypair.sign_message(message.to_bytes_versioned(raw_transaction.message))
            return {
                "result": bytes(signature).hex()
            }
        else:
            t = Transaction.deserialize(bytes.fromhex(transaction))
            # 某些transation需要一个额外的临时签名
            # some transactions need an extra signature
            if void_keypair:
                void_keypair = Keypair.from_json(void_keypair)
                t.sign(wallet_keypair, void_keypair)
            else:
                t.sign(wallet_keypair)
                
            signed_tx = t.serialize()

            return {
                "result": signed_tx.hex()
            }
