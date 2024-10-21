from shield.shield import SHIELD
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.transaction import Transaction

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
    
    t = Transaction.deserialize(bytes.fromhex(transaction))
    
    # 只允许两种交易
    # Only two types of transactions are allowed
    if function not in ["jlp_mint_or_burn_sign", "transfer"]:
        return {
            "error": "Invalid function"
        }
    
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
                 
    return {
        "status": "ok"
    }


def sign_transaction(transaction, void_keypair):
    with SHIELD.get_private_key() as pk:
        if not pk:
            return {
                "error": "Address not found"
            }
    
        wallet_keypair = Keypair.from_base58_string(pk)
        
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
