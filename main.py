import os
import json
import uuid
import random
import asyncio
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import (
    NFTokenMint,
    Payment,
    NFTokenCreateOffer,
    NFTokenAcceptOffer
)
from xrpl.models.requests import AccountNFTs
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops, str_to_hex
import xrpl

from json_db import init_db, read_db, write_db

# Initialize environment and app
load_dotenv()
app = FastAPI()
init_db()

# Configuration
TESTNET_URL = "https://s.altnet.rippletest.net:51234/"  # Using altnet consistently
XRPL_CLIENT = JsonRpcClient(TESTNET_URL)

# Wallets
MERCHANT_SEED = os.getenv("MERCHANT_SEED", "sEdT9mpowZY1gUbqUCybBzfzp2xwFfD")  # From env or default
MERCHANT_WALLET = Wallet.from_seed(MERCHANT_SEED)
MINTER_SEED = os.getenv("MINTER_SEED")

# Thread pool for synchronous operations
executor = ThreadPoolExecutor()

# Helper function to run sync XRPL operations
async def run_sync_xrpl_operation(sync_func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, sync_func, *args)

# --------------------------
# Account Management Endpoints
# --------------------------

class AccountRequest(BaseModel):
    seed: str = ""

class PaymentRequest(BaseModel):
    seed: str
    amount: int
    destination: str

@app.post("/get_account")
def api_get_account(req: AccountRequest):
    """Create or recover a wallet"""
    try:
        wallet = get_account(req.seed)
        return {
            "accountId": wallet.classic_address,
            "seed": wallet.seed,
            "public_key": wallet.public_key
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get_account_info/{account_id}")
def api_get_account_info(account_id: str):
    """Get account info"""
    try:
        return get_account_info(account_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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

# --------------------------
# NFT Ticket Endpoints
# --------------------------

class TicketPurchase(BaseModel):
    buyer_wallet_address: str
    event_id: str
    quantity: int
    payment_currency: str = "RLUSD"

class NFTTicket(BaseModel):
    ticket_id: str
    event_id: str
    owner_address: str
    seat_number: str

class EventCreate(BaseModel):
    name: str
    total_tickets: int
    price_rlusd: float
    organizer_wallet: str

@app.post("/create-ticket")
async def create_ticket(
    event_name: str,
    ticket_price: float,
    supply: int = 1
):
    """Endpoint to create NFT tickets"""
    try:
        nft_tx_hashes = await run_sync_xrpl_operation(
            sync_create_ticket,
            event_name,
            ticket_price,
            supply
        )
        return {
            "event": event_name,
            "price": ticket_price,
            "nft_tx_hashes": nft_tx_hashes
        }
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/buy-ticket")
async def buy_ticket(buyer_seed: str, nft_id: str, price: float):
    """Endpoint to purchase a ticket"""
    try:
        result = await run_sync_xrpl_operation(
            sync_buy_ticket,
            buyer_seed,
            nft_id,
            price
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/purchase_ticket")
async def purchase_ticket(purchase: TicketPurchase):
    """Purchase ticket with RLUSD payment"""
    try:
        # 1. Check inventory
        db = read_db()
        event = next((e for e in db["events"] if e["id"] == purchase.event_id), None)
        
        if not event:
            raise HTTPException(404, "Event not found")
        if event["tickets_sold"] + purchase.quantity > event["total_tickets"]:
            raise HTTPException(400, "Not enough tickets")
        
        # 2. Process payment 
        payment_status = await _mock_process_rlusd_payment(
            purchase.buyer_wallet_address,
            purchase.quantity * event["price_rlusd"]
        )
        
        # 3. Mint NFTs
        nft_ticket = await _mint_nft_ticket(
            event_id=purchase.event_id,
            owner_address=purchase.buyer_wallet_address
        )
        
        # 4. Update JSON DB
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
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/create_event")
def create_event(event: EventCreate):
    """Create new event"""
    try:
        db = read_db()
        new_event = {
            "id": str(uuid.uuid4()),
            **event.dict(),
            "tickets_sold": 0
        }
        db["events"].append(new_event)
        write_db(db)
        return {"event_id": new_event["id"]}
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/events/{event_id}/availability")
def check_availability(event_id: str):
    """Check ticket availability"""
    try:
        db = read_db()
        event = next((e for e in db["events"] if e["id"] == event_id), None)
        if not event:
            raise HTTPException(404, "Event not found")
        return {
            "available": event['total_tickets'] - event['tickets_sold'],
            "price_per_ticket": event['price_rlusd']
        }
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/events")
def list_events():
    """List all events"""
    try:
        db = read_db()
        return db["events"]
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/account-nfts/{account}", response_model=List[Dict])
def get_account_nfts(account: str):
    """Get all NFTs for an account"""
    try:
        # Initial request
        response = XRPL_CLIENT.request(
            AccountNFTs(account=account, limit=400)
        )
        
        if not response.is_successful():
            raise HTTPException(400, "XRPL request failed")

        all_nfts = []
        nfts = response.result.get("account_nfts", [])
        all_nfts.extend(nfts)
        
        # Handle pagination
        marker = response.result.get("marker")
        while marker:
            next_page = XRPL_CLIENT.request(
                AccountNFTs(account=account, limit=400, marker=marker)
            )
            if not next_page.is_successful():
                break
                
            nfts = next_page.result.get("account_nfts", [])
            all_nfts.extend(nfts)
            marker = next_page.result.get("marker")

        return all_nfts
    except Exception as e:
        raise HTTPException(500, str(e))

# --------------------------
# Helper Functions
# --------------------------

def get_account(seed: str) -> Wallet:
    """Get or create wallet"""
    if not seed:
        return xrpl.wallet.generate_faucet_wallet(XRPL_CLIENT)
    return Wallet.from_seed(seed)

def get_account_info(account_id: str) -> Dict:
    """Get account info from XRPL"""
    acct_info = xrpl.models.requests.account_info.AccountInfo(
        account=account_id,
        ledger_index="validated"
    )
    response = XRPL_CLIENT.request(acct_info)
    return response.result['account_data']

def send_xrp(seed: str, amount: int, destination: str):
    """Send XRP payment"""
    sending_wallet = Wallet.from_seed(seed)
    payment = Payment(
        account=sending_wallet.classic_address,
        amount=xrp_to_drops(amount),
        destination=destination,
    )
    try:    
        return submit_and_wait(payment, XRPL_CLIENT, sending_wallet)
    except xrpl.transaction.XRPLReliableSubmissionException as e:    
        return f"Submit failed: {e}"

def sync_create_ticket(event_name: str, ticket_price: float, supply: int = 1):
    """Synchronous NFT ticket creation"""
    nfts = []
    for _ in range(supply):
        mint_tx = NFTokenMint(
            account=MERCHANT_WALLET.classic_address,
            flags=8,
            nftoken_taxon=0
        )
        result = submit_and_wait(mint_tx, XRPL_CLIENT, MERCHANT_WALLET)
        nfts.append(result.result["hash"])
    return nfts

def sync_buy_ticket(buyer_seed: str, nft_id: str, price: float):
    """Synchronous ticket purchase"""
    buyer_wallet = Wallet.from_seed(buyer_seed)
    
    # Verify NFT exists
    nft_info = XRPL_CLIENT.request(
        AccountNFTs(account=MERCHANT_WALLET.classic_address)
    )
   
    if not any(nft["NFTokenID"] == nft_id for nft in nft_info.result["account_nfts"]):
        raise ValueError("NFT not available")

    # Create sell offer
    offer_tx = NFTokenCreateOffer(
        account=MERCHANT_WALLET.classic_address,
        nftoken_id=nft_id,
        amount=xrp_to_drops(price),
        flags=1,
        destination=buyer_wallet.classic_address
    )
    offer_response = submit_and_wait(offer_tx, XRPL_CLIENT, MERCHANT_WALLET)
    
    if "meta" not in offer_response.result or "offer_id" not in offer_response.result["meta"]:
        raise ValueError("Could not determine offer ID")
    
    offer_id = offer_response.result["meta"]["offer_id"]
    
    # Buyer accepts offer
    accept_tx = NFTokenAcceptOffer(
        account=buyer_wallet.classic_address,
        nftoken_sell_offer=offer_id
    )
    response = submit_and_wait(accept_tx, XRPL_CLIENT, buyer_wallet)
    
    return {
        "status": "success",
        "tx_hash": response.result["hash"]
    }

async def _mock_process_rlusd_payment(sender: str, amount: float):
    """Mock RLUSD payment processor"""
    return {"status": "success", "tx_hash": "0x123..."}

async def _mint_nft_ticket(event_id: str, owner_address: str):
    """Mint NFT ticket with seat data"""
    ticket_data = {
        "event_id": event_id,
        "seat": f"{random.randint(1, 100)}-{random.randint(1, 50)}"
    }

    minter_wallet = Wallet.from_seed(MINTER_SEED)
    nft_tx = NFTokenMint(
        account=minter_wallet.classic_address,
        uri=str_to_hex(json.dumps(ticket_data)),
        nftoken_taxon=0,
        flags=1
    )
    response = submit_and_wait(nft_tx, XRPL_CLIENT, minter_wallet)
    
    return {
        "nft_id": response.result["NFTokenID"],
        "ticket_data": ticket_data
    }