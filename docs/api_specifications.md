# API Specifications (Core Banking & MCP Tools)

## 1. ValidateAccountAPI
- **Purpose**: Verify account existence and active standing.
- **Request**:
  ```json
  {
    "account_number": "1234567890"
  }
  ```
- **Response**:
  ```json
  {
    "status": "VALID",
    "customer_name": "John Doe",
    "account_type": "Savings Account"
  }
  ```

## 2. ValidateCardAPI
- **Purpose**: Verify credit card number validity.
- **Request**:
  ```json
  {
    "card_number": "4567XXXX8901"
  }
  ```
- **Response**:
  ```json
  {
    "status": "VALID",
    "card_type": "Regalia Gold Credit Card",
    "card_holder": "John Doe"
  }
  ```

## 3. GetAccountBalanceAPI
- **Purpose**: Fetch current balance.
- **Request**:
  ```json
  {
    "account_number": "1234567890"
  }
  ```
- **Response**:
  ```json
  {
    "status": "SUCCESS",
    "account_number": "1234567890",
    "balance": 125000.0,
    "currency": "INR",
    "account_type": "Savings Account"
  }
  ```

## 4. GetCardTransactionsAPI
- **Purpose**: Retrieve recent credit card transactions.
- **Request**:
  ```json
  {
    "card_number": "4567XXXX8901",
    "limit": 5
  }
  ```
- **Response**:
  ```json
  {
    "status": "SUCCESS",
    "card_number": "4567XXXX8901",
    "transactions": [
      {
        "id": "TXN-901",
        "date": "2026-05-02",
        "merchant": "Amazon India",
        "amount": 4299.0,
        "type": "DEBIT",
        "status": "SUCCESS"
      }
    ],
    "total_returned": 1
  }
  ```

## 5. GetStatementAPI
- **Purpose**: Retrieve account statement for a period.
- **Request**:
  ```json
  {
    "account_number": "1234567890",
    "period": "April 2026"
  }
  ```
- **Response**:
  ```json
  {
    "status": "SUCCESS",
    "account_number": "1234567890",
    "period": "April 2026",
    "statement_id": "STMT-202604-1234567890",
    "download_url": "https://netbanking.hdfcbank.com/statements/STMT-202604-1234567890.pdf"
  }
  ```

