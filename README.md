# swisshacks-BE

# XRPL API Documentation

## Overview
This API provides endpoints for interacting with the XRP Ledger Testnet. It handles wallet creation, account information retrieval, and XRP transfers.

## Endpoints

### 1. Create/Recover Wallet
`POST /get_account`

Request Body:
```json
{
  "seed": "string"  // Empty string for new wallet, existing seed for recovery
}
```

Response:
```json
{
  "accountId": "string",
  "seed": "string",
  "public_key": "string"
}
```

### 2. Get Account Information
`GET /get_account_info/{account_id}`

Path Parameters:
- `account_id`: XRP Ledger address

Response:
```json
{
  "Account": "string",           // The account address
  "Balance": "string",          // Account balance in drops (1 XRP = 1,000,000 drops)
  "Flags": number,              // Account flags (0 = no flags)
  "LedgerEntryType": "string",  // Type of ledger entry ("AccountRoot")
  "OwnerCount": number,         // Number of trust lines and offers
  "PreviousTxnID": "string",    // Hash of previous transaction
  "PreviousTxnLgrSeq": number,  // Sequence number of previous ledger
  "Sequence": number,           // Next sequence number for transaction
  "index": "string"             // Ledger index of this account
}
```

### 3. Send XRP
`POST /send_xrp`

Request Body:
```json
{
  "seed": "string",
  "amount": "number",
  "destination": "string"
}
```

Response:
```json
{
  "tx_hash": "string"
}
```

## Error Handling
All endpoints return standard HTTP status codes:
- 200: Success
- 400: Invalid request or error
- Error responses include a `detail` field with the error message

## Usage Example
```bash
# Create new wallet
curl -X POST http://localhost:8000/get_account \
  -H "Content-Type: application/json" \
  -d '{"seed": ""}'

# Get account info
curl http://localhost:8000/get_account_info/r12345

# Send XRP
curl -X POST http://localhost:8000/send_xrp \
  -H "Content-Type: application/json" \
  -d '{"seed": "your_seed", "amount": 1000000, "destination": "r12345"}'
```

## Important Notes
- All amounts are in drops (1 XRP = 1,000,000 drops)
- This API uses the XRP Ledger Testnet
- Always store seeds securely
- Error messages are detailed for debugging purposes