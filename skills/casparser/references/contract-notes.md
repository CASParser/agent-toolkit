# Contract Note Parsing

## Overview

Contract notes are legal documents from SEBI-registered brokers that detail all trades executed by an investor on a given day. CAS Parser extracts structured data from these PDFs.

## Supported Brokers

| Broker | `broker_type` | Auto-Detected |
|--------|---------------|---------------|
| Zerodha Broking Limited | `zerodha` | Yes |
| Groww Invest Tech Private Limited | `groww` | Yes |
| Upstox (RKSV Securities) | `upstox` | Yes |
| ICICI Securities Limited | `icici` | Yes |

The API auto-detects the broker from the PDF content. You can optionally pass `broker_type` to override auto-detection.

## Endpoint

```
POST /v4/contract_note/parse
```

### File Upload
```
POST /v4/contract_note/parse
x-api-key: your-api-key
Content-Type: multipart/form-data

pdf_file: <binary file>
password: ABCDE1234F
broker_type: zerodha  (optional)
```

### JSON Body
```json
{
  "pdf_url": "https://example.com/contract_note.pdf",
  "password": "ABCDE1234F",
  "broker_type": "zerodha"
}
```

## Password

Contract note passwords are typically the **client's PAN number** (10-character alphanumeric, e.g., `ABCDE1234F`).

## Response Structure

```json
{
  "status": "success",
  "msg": "success",
  "data": {
    "contract_note_info": {
      "contract_note_number": "CNT-25/26-73436720",
      "trade_date": "2025-08-05",
      "settlement_number": "2025149",
      "settlement_date": "2025-08-06"
    },
    "broker_info": {
      "broker_type": "zerodha",
      "name": "Zerodha Broking Limited",
      "sebi_registration": "INZ000031633"
    },
    "client_info": {
      "name": "VIRENDER KUMAR",
      "pan": "FAXAK2545F",
      "ucc": "YS3654",
      "place_of_supply": "DELHI",
      "gst_state_code": "7",
      "address": "..."
    },
    "equity_transactions": [ ... ],
    "derivatives_transactions": [ ... ],
    "detailed_trades": [ ... ],
    "charges_summary": { ... }
  }
}
```

### `equity_transactions[]`

Summary of equity transactions grouped by security:

```json
{
  "isin": "INE172A01027",
  "security_name": "CASTROLIND",
  "security_symbol": "CASTROLIND",
  "buy_quantity": 10,
  "buy_wap": 195.50,
  "buy_total_value": 1955.00,
  "sell_quantity": 0,
  "sell_wap": 0,
  "sell_total_value": 0,
  "net_obligation": -1955.00
}
```

### `detailed_trades[]`

Individual trade-by-trade breakdown:

```json
{
  "order_number": "1000000042939390",
  "order_time": "13:13:13",
  "trade_number": "4006567",
  "trade_time": "13:13:13",
  "security_description": "CASTROLIND-EQ/INE172A01027",
  "buy_sell": "B",
  "exchange": "NSE",
  "quantity": 10,
  "brokerage": 0,
  "net_rate_per_unit": 195.50,
  "closing_rate_per_unit": 195.50,
  "net_total": 1955.00,
  "remarks": ""
}
```

### `charges_summary`

```json
{
  "pay_in_pay_out_obligation": -1955.00,
  "taxable_value_brokerage": 0,
  "exchange_transaction_charges": 0.67,
  "cgst": 0.06,
  "sgst": 0.06,
  "igst": 0,
  "securities_transaction_tax": 1.96,
  "sebi_turnover_fees": 0.02,
  "stamp_duty": 0.29,
  "net_amount_receivable_payable": -1958.06
}
```

## Use Cases

- **Trade reconciliation** — Match broker trades with demat holdings
- **Tax computation** — Calculate capital gains/losses using actual trade prices
- **Brokerage analysis** — Track trading costs across brokers
- **Compliance** — Audit trail for regulatory requirements

## Related Templates

- [`templates/python-contract-note.py`](../templates/python-contract-note.py)
- [`templates/curl-examples.sh`](../templates/curl-examples.sh) (section 4)
