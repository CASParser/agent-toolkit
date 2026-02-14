# Unified Response Format

All CAS parse endpoints return the same unified structure, regardless of CAS type.

## Top-Level Structure

```json
{
  "meta": { ... },
  "investor": { ... },
  "summary": { ... },
  "demat_accounts": [ ... ],
  "mutual_funds": [ ... ],
  "insurance": { ... },
  "nps": [ ... ]
}
```

## `meta`

```json
{
  "cas_type": "CDSL | NSDL | CAMS_KFINTECH",
  "statement_period": {
    "from": "2025-01-01",
    "to": "2025-12-31"
  },
  "generated_at": "2025-12-15T10:30:00Z"
}
```

## `investor`

```json
{
  "name": "John Doe",
  "pan": "ABCDE1234F",
  "email": "john@example.com",
  "address": "123 Main Street, Mumbai",
  "pincode": "400001",
  "mobile": "9876543210",
  "cas_id": "CAS-12345"
}
```

`cas_id` is only present for NSDL and CDSL CAS types.

## `summary`

```json
{
  "total_value": 1500000.00,
  "accounts": {
    "demat": { "count": 2, "total_value": 800000.00 },
    "mutual_funds": { "count": 5, "total_value": 500000.00 },
    "insurance": { "count": 1, "total_value": 150000.00 },
    "nps": { "count": 1, "total_value": 50000.00 }
  }
}
```

## `demat_accounts[]`

Each demat account:

```json
{
  "demat_type": "NSDL | CDSL",
  "dp_id": "IN300476",
  "dp_name": "Zerodha Broking Ltd",
  "client_id": "12345678",
  "bo_id": "1234567890123456",
  "value": 500000.00,
  "linked_holders": [
    { "name": "John Doe", "pan": "ABCDE1234F" }
  ],
  "holdings": {
    "equities": [
      {
        "isin": "INE002A01018",
        "name": "Reliance Industries Limited",
        "units": 10.0,
        "value": 25000.00,
        "transactions": [ ... ],
        "additional_info": {
          "open_units": 10.0,
          "close_units": 10.0
        }
      }
    ],
    "corporate_bonds": [
      {
        "isin": "INE123A07890",
        "name": "HDFC Ltd Bond 8.5%",
        "units": 5.0,
        "value": 52500.00,
        "additional_info": {
          "coupon_rate": "8.5%",
          "maturity_date": "2027-06-30",
          "face_value": 1000,
          "market_value": 1050
        }
      }
    ],
    "government_securities": [ ... ],
    "aifs": [ ... ],
    "demat_mutual_funds": [ ... ]
  },
  "additional_info": {
    "bo_status": "Active",
    "email": "john@example.com",
    "nominee": "Jane Doe"
  }
}
```

## `mutual_funds[]`

Each mutual fund folio:

```json
{
  "folio_number": "1234567890",
  "amc": "HDFC Mutual Fund",
  "registrar": "CAMS",
  "value": 100000.00,
  "linked_holders": [
    { "name": "John Doe", "pan": "ABCDE1234F" }
  ],
  "schemes": [
    {
      "isin": "INF179KA1YQ1",
      "name": "HDFC Flexi Cap Fund - Growth",
      "type": "Equity",
      "units": 50.5,
      "nav": 1500.00,
      "value": 75750.00,
      "cost": 60000.00,
      "gain": {
        "absolute": 15750.00,
        "percentage": 26.25
      },
      "transactions": [
        {
          "date": "2025-01-15",
          "description": "Purchase - SIP",
          "type": "PURCHASE_SIP",
          "amount": 5000.00,
          "units": 3.33,
          "nav": 1500.00,
          "balance": 50.5,
          "dividend_rate": null
        }
      ],
      "nominees": ["Jane Doe"],
      "additional_info": {
        "advisor": "Direct",
        "rta_code": "HDF2345",
        "amfi": "135832",
        "open_units": 47.17,
        "close_units": 50.5
      }
    }
  ],
  "additional_info": {
    "pan": "ABCDE1234F",
    "pankyc": "OK",
    "kyc": "OK"
  }
}
```

## `insurance`

```json
{
  "life_insurance_policies": [
    {
      "policy_number": "POL123456",
      "provider": "LIC of India",
      "policy_name": "Jeevan Anand",
      "life_assured": "John Doe",
      "status": "Active",
      "sum_assured": 1000000.00,
      "premium_amount": 25000.00,
      "premium_frequency": "Annual"
    }
  ]
}
```

## `nps[]` (NSDL only)

```json
[
  {
    "pran": "110012345678",
    "cra": "NSDL CRA",
    "value": 50000.00,
    "funds": [
      {
        "name": "SBI Pension Fund - Tier I - E",
        "units": 100.0,
        "nav": 500.00,
        "value": 50000.00,
        "cost": 45000.00,
        "additional_info": {
          "tier": 1,
          "manager": "SBI Pension Funds"
        }
      }
    ],
    "linked_holders": [
      { "name": "John Doe", "pan": "ABCDE1234F" }
    ]
  }
]
```

## Transaction Types

All transaction `type` fields use these standardized values:

| Type | Description |
|------|-------------|
| `PURCHASE` | Lump sum purchase |
| `PURCHASE_SIP` | Systematic Investment Plan purchase |
| `REDEMPTION` | Units sold/redeemed |
| `SWITCH_IN` | Units received from another scheme |
| `SWITCH_IN_MERGER` | Units received from scheme merger |
| `SWITCH_OUT` | Units transferred to another scheme |
| `SWITCH_OUT_MERGER` | Units transferred due to scheme merger |
| `DIVIDEND_PAYOUT` | Dividend paid out |
| `DIVIDEND_REINVEST` | Dividend reinvested |
| `SEGREGATION` | Segregated portfolio creation |
| `STAMP_DUTY_TAX` | Stamp duty deduction |
| `TDS_TAX` | TDS deduction |
| `STT_TAX` | Securities Transaction Tax |
| `MISC` | Miscellaneous transaction |
| `REVERSAL` | Transaction reversal |
| `UNKNOWN` | Unclassified transaction |
