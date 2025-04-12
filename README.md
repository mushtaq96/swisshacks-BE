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


Here's the README documentation for the events functionality:

# Events API Documentation

## Overview

This API provides endpoints for creating, managing, and purchasing event tickets on the XRP Ledger Testnet. It implements a ticketing system using NFTs (Non-Fungible Tokens) to represent unique event tickets.

## Endpoints

### 1. Create New Event

```http
POST /create_event
```

Request Body:

```json
{
  "name": "string",           // Event name
  "total_tickets": "number",  // Total number of tickets available
  "price_rlusd": "number",   // Price per ticket in RLUSD
  "organizer_wallet": "string" // Organizer's XRP Ledger address
}
```

Response:

```json
{
  "event_id": "string"  // Unique identifier for the event
}
```

### 2. Purchase Tickets

```http
POST /purchase_ticket
```

Request Body:

```json
{
  "event_id": "string",           // ID of the event
  "buyer_wallet_address": "string", // Buyer's XRP Ledger address
  "quantity": "number",           // Number of tickets to purchase
  "payment_currency": "string"    // Currency for payment (default: "RLUSD")
}
```

Response:

```json
{
  "payment_status": {
    "status": "string",
    "tx_hash": "string"
  },
  "nft_ticket": {
    "nft_id": "string",
    "ticket_data": {
      "event_id": "string",
      "seat": "string"
    }
  }
}
```

### 3. Check Event Availability

```http
GET /events/{event_id}/availability
```

Path Parameters:

- `event_id`: The ID of the event to check

Response:

```json
{
  "available": "number",         // Number of tickets still available
  "price_per_ticket": "number"  // Price per ticket in RLUSD
}
```

## Error Handling

All endpoints return standard HTTP status codes:

- 200: Success
- 400: Invalid request or error
- 404: Event not found

Error responses include a `detail` field with the error message.

## Usage Examples

1. Create a new event:

```bash
curl -X POST http://localhost:8000/create_event \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Concert 2025",
    "total_tickets": 100,
    "price_rlusd": 50.0,
    "organizer_wallet": "r12345"
  }'
```

2. Purchase tickets:

```bash
curl -X POST http://localhost:8000/purchase_ticket \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "event_123",
    "buyer_wallet_address": "r67890",
    "quantity": 2
  }'
```

3. Check event availability:

```bash
curl http://localhost:8000/events/event_123/availability
```

## Important Notes

- All tickets are represented as unique NFTs on the XRP Ledger
- Each ticket includes a randomly assigned seat number
- The API uses the XRP Ledger Testnet for all operations
- Payment processing is currently mocked (replace `_mock_process_rlusd_payment` with actual RLUSD transaction logic)
- Store wallet seeds securely
- Error messages are detailed for debugging purposes

The API provides a complete ticketing system with NFT-based ticket representation, ensuring unique ownership and transferability of event tickets on the XRP Ledger.