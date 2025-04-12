from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xrpl

app = FastAPI()
testnet_url = "https://s.devnet.rippletest.net:51234/"

# Request models
class AccountRequest(BaseModel):
    seed: str = ""

class PaymentRequest(BaseModel):
    seed: str
    amount: int
    destination: str

# Endpoints
@app.post("/get_account")
def api_get_account(req: AccountRequest):
    """Create or recover a wallet"""
    try:
        wallet = get_account(req.seed)
        return {
            "accountId": wallet.address,
            "seed": wallet.seed,
            "public_key": wallet.public_key
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# endpoint to get account info
@app.get("/get_account_info/{account_id}")
def api_get_account_info(account_id: str):
    """Get account info """
    try:
        return get_account_info(account_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# endpoint to send xrp
@app.post("/send_xrp")
def api_send_xrp(req: PaymentRequest):
    """Send XRP"""
    try:
        result = send_xrp(req.seed, req.amount, req.destination)
        if isinstance(result, str):  # Error case
            raise HTTPException(status_code=400, detail=result)
        return {"tx_hash": result.result["hash"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#  Helper functions 
def get_account(seed):
    """get_account"""
    client = xrpl.clients.JsonRpcClient(testnet_url)
    if (seed == ''):
        new_wallet = xrpl.wallet.generate_faucet_wallet(client)
    else:
        new_wallet = xrpl.wallet.Wallet.from_seed(seed)
    return new_wallet

def get_account_info(accountId):
    """get_account_info"""
    client = xrpl.clients.JsonRpcClient(testnet_url)
    acct_info = xrpl.models.requests.account_info.AccountInfo(
        account=accountId,
        ledger_index="validated"
    )
    response = client.request(acct_info)
    return response.result['account_data']

def send_xrp(seed, amount, destination):
    sending_wallet = xrpl.wallet.Wallet.from_seed(seed)
    client = xrpl.clients.JsonRpcClient(testnet_url)
    payment = xrpl.models.transactions.Payment(
        account=sending_wallet.address,
        amount=xrpl.utils.xrp_to_drops(int(amount)),
        destination=destination,
    )
    try:    
        response = xrpl.transaction.submit_and_wait(payment, client, sending_wallet)    
    except xrpl.transaction.XRPLReliableSubmissionException as e:    
        response = f"Submit failed: {e}"
    return response