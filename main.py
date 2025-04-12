from xrpl.transaction import submit_and_wait
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xrpl
import random
from json_db import init_db, read_db, write_db
from fastapi import FastAPI
import uuid
from xrpl.models.requests import AccountNFTs
from xrpl.wallet import Wallet
from dotenv import load_dotenv
import os
from xrpl.utils import str_to_hex
import json
from xrpl.clients import JsonRpcClient

load_dotenv()  # Add at the top of your main.py


app = FastAPI()
init_db() 


testnet_url = "https://s.devnet.rippletest.net:51234/"
xrpl_client = JsonRpcClient(testnet_url)

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



# Pydantic Models
class TicketPurchase(BaseModel):
    buyer_wallet_address: str  # Frontend provides this
    event_id: str
    quantity: int
    payment_currency: str = "RLUSD"

class NFTTicket(BaseModel):
    ticket_id: str
    event_id: str
    owner_address: str
    seat_number: str

# Endpoints
@app.post("/purchase_ticket")
async def purchase_ticket(purchase: TicketPurchase):
    # 1. Check inventory (using JSON "DB")
    db = read_db()
    event = next((e for e in db["events"] if e["id"] == purchase.event_id), None)
    
    if not event:
        raise HTTPException(404, "Event not found")
    if event["tickets_sold"] + purchase.quantity > event["total_tickets"]:
        raise HTTPException(400, "Not enough tickets")
    
    # 2. Process payment 
    payment_status = await _mock_process_rlusd_payment(
        purchase.buyer_wallet_address,
        purchase.quantity * 50
    )
    
    # 3. Mint NFTs (unchanged)
    nft_ticket = await _mint_nft_ticket(
        event_id=purchase.event_id,
        owner_address=purchase.buyer_wallet_address
    )
    
    # 4. Update JSON "DB"
    event["tickets_sold"] += purchase.quantity
    db["tickets"].append({
        "nft_id": nft_ticket["nft_id"],
        "event_id": purchase.event_id,
        "owner": purchase.buyer_wallet_address,
        "seat": nft_ticket["ticket_data"]["seat"]
    })
    write_db(db)
    
    return {
        "payment_status": payment_status,
        "nft_ticket": nft_ticket
    }

# Helper Functions
async def _mock_process_rlusd_payment(sender: str, amount: float):
    """Replace with real RLUSD transaction later"""
    return {"status": "success", "tx_hash": "0x123..."}

async def _mint_nft_ticket(event_id: str, owner_address: str):
    """Mint NFT ticket on XRPL"""
    ticket_data = {
        "event_id": event_id,
        "seat": f"{random.randint(1, 100)}-{random.randint(1, 50)}"  # Random seat
    }

    seed = os.getenv("MINTER_SEED")
    minter_wallet=xrpl.wallet.Wallet.from_seed(seed)
    nft_tx = xrpl.models.transactions.NFTokenMint(
        account=minter_wallet.address,
        uri=str_to_hex(json.dumps(ticket_data)),
        nftoken_taxon=0,
        flags=1  # Transferable
    )
    response = submit_and_wait(nft_tx, xrpl_client, minter_wallet)
    
    return {
        "nft_id": response.result["NFTokenID"],
        "ticket_data": ticket_data
    }

class EventCreate(BaseModel):
    name: str
    total_tickets: int
    price_rlusd: float
    organizer_wallet: str

# Endpoint to create a new event
@app.post("/create_event")
def create_event(event: EventCreate):
    """For organizers to list new events"""
    db = read_db()
    new_event = {
        "id": str(uuid.uuid4()),
        **event.dict(),
        "tickets_sold": 0
    }
    db["events"].append(new_event)
    write_db(db)
    return {"event_id": new_event["id"]}

# Endpoint to get specific event details
@app.get("/events/{event_id}/availability")
def check_availability(event_id: str):
    db = read_db()
    event = next((e for e in db["events"] if e["id"] == event_id), None)
    print(event)
    return {
        "available": event['total_tickets'] - event['tickets_sold'],
        "price_per_ticket": event['price_rlusd']
    }
# Endpoint to get all events
@app.get("/events")
def list_events():
    """Get all available events"""
    db = read_db()
    return db["events"]