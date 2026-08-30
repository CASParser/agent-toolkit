# Registry Verification — SEBI & AMFI

Confirm a financial intermediary is genuinely registered with its regulator, in one call, before onboarding. Two endpoints, both a yes/no gate:

| Endpoint | Verifies | Register |
|----------|----------|----------|
| `POST /v1/verify/sebi` | Any SEBI intermediary (RIA, RA, PMS, broker, MF, AIF, …) | SEBI recognised-intermediaries |
| `POST /v1/verify/mfd` | Mutual Fund Distributor by ARN | AMFI distributor register + adverse lists |

Both are `POST` + JSON, authenticated with `x-api-key`. **0.25 credits** per successful verification — a "not found" is a successful `200` and is billed; only upstream failures return `5xx` (free). Billed under a single `verify` feature; the register hit (SEBI/AMFI) is recorded on the usage event.

---

## `POST /v1/verify/sebi`

### Request

Provide **`registration_number`**, or **`name` + `type`**.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `registration_number` | string | one of | e.g. `INA000000888`. Category auto-detected. Authoritative — a `name` sent with it is ignored. |
| `name` | string | one of | Trade/entity name. Requires `type`. Substring search; the first match is returned. |
| `type` | string | with `name`, or for fund/FPI numbers | Category slug (below). Also overrides detection. |

Input contract: `{registration_number}` **or** `{name, type}`. Neither → `400`. A `registration_number` whose category can't be detected and no `type` → `422`.

### Category detection

The letter after `IN` selects the category — no `type` needed:

| Prefix | slug |
|--------|------|
| `INA` | `investment-adviser` |
| `INH` | `research-analyst` |
| `INP` | `portfolio-manager` |
| `INM` | `merchant-banker` |
| `INR` | `registrar-transfer-agent` |
| `INB` `INE` `INF` `INZ` | `stock-broker` |

All other registers need an explicit `type` (their numbers don't encode a category):

`mutual-fund`, `alternative-investment-fund`, `credit-rating-agency`, `custodian`, `debenture-trustee`, `venture-capital-fund`, `foreign-venture-capital-investor`, `foreign-portfolio-investor`, `kyc-registration-agency`, `infrastructure-investment-trust`, `real-estate-investment-trust`, `esg-rating-provider`, `vault-manager`.

Aliases: `ria`/`ia` → investment-adviser, `ra` → research-analyst, `pms` → portfolio-manager, `broker` → stock-broker, `rta` → registrar-transfer-agent, `mf` → mutual-fund, `aif`, `cra`, `vcf`, `fvci`, `fpi`, `kra`, `invit`, `reit`.

### Response

Every key is always present on `200` (`null` when N/A). `verified` is the gate.

| Field | Type | Notes |
|-------|------|-------|
| `status` | string | `"success"` |
| `verified` | bool | `true` only when a registration is found **and** `ACTIVE` |
| `authority` | string | `"SEBI"` |
| `category` | string | resolved slug |
| `category_label` | string | human label, e.g. `Portfolio Manager (PMS)` |
| `registration_number` | string\|null | echoed / from the register |
| `name` | string\|null | registered legal/trade name |
| `registration_status` | string | `ACTIVE` \| `EXPIRED` \| `NOT_FOUND` |
| `valid_from` | date\|null | ISO date |
| `valid_till` | date\|null | `null` when perpetual |
| `is_perpetual` | bool | most SEBI registrations are perpetual |
| `address`, `email`, `telephone`, `contact_person` | string\|null | from the register; vary by category |
| `detected_by` | string | `registration_number` \| `type` |

```bash
curl -s https://api.casparser.in/v1/verify/sebi \
  -H "x-api-key: $CASPARSER_API_KEY" -H "Content-Type: application/json" \
  -d '{"registration_number":"INP000000670"}'
```

---

## `POST /v1/verify/mfd`

### Request

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `arn` | string | yes | Digits; an `ARN-` prefix is tolerated. **Exact match only** — a partial ARN returns `NOT_FOUND`, never another distributor. |

### Adverse-list screening

Every ARN + its EUIN is checked against three AMFI lists. A hit sets `negative_list` and overrides `registration_status`:

| `negative_list.type` | Source list | `registration_status` |
|----------------------|-------------|----------------------|
| `suspended` | ARN suspended from MF business | `SUSPENDED` |
| `terminated` | ARN terminated | `TERMINATED` |
| `euin_terminated` | EUIN under the ARN terminated | `TERMINATED` |

`negative_list.since` = effective date AMFI published.

### Response

| Field | Type | Notes |
|-------|------|-------|
| `status` | string | `"success"` |
| `verified` | bool | `true` only when active **and** not on an adverse list |
| `authority` | string | `"AMFI"` |
| `category` | string | `"mutual-fund-distributor"` |
| `category_label` | string | `Mutual Fund Distributor (ARN)` |
| `arn` | string | normalized digits |
| `name` | string\|null | ARN holder name |
| `euin` | string\|null | Employee Unique Identification Number |
| `kyd_compliant` | bool\|null | Know Your Distributor status |
| `registration_status` | string | `ACTIVE` \| `EXPIRED` \| `SUSPENDED` \| `TERMINATED` \| `NOT_FOUND` |
| `valid_from`, `valid_till` | date\|null | ARN validity window (never perpetual) |
| `is_perpetual` | bool | always `false` for ARNs |
| `address`, `pincode` | string\|null | from the register |
| `negative_list_hit` | bool | `true` when on any adverse list |
| `negative_list` | object\|null | `{ type, since }` on a hit, else `null` |

```bash
curl -s https://api.casparser.in/v1/verify/mfd \
  -H "x-api-key: $CASPARSER_API_KEY" -H "Content-Type: application/json" \
  -d '{"arn":"89762"}'
```

---

## `registration_status` semantics

| Status | Meaning | `verified` | Authority |
|--------|---------|-----------|-----------|
| `ACTIVE` | Currently registered, in good standing | `true` | both |
| `EXPIRED` | Validity end date has passed | `false` | both |
| `SUSPENDED` | On AMFI's suspended list | `false` | AMFI |
| `TERMINATED` | On AMFI's terminated / EUIN-terminated list | `false` | AMFI |
| `NOT_FOUND` | No current registration in this register | `false` | both |

## Errors

| HTTP | Cause | Retryable |
|------|-------|-----------|
| `400` | Missing input, unknown `type`, or `name` without `type` | No |
| `401` | Invalid/missing API key | No |
| `403` | `verify` not on your plan, or quota exhausted | No |
| `422` | Category undetectable from the number — pass `type` | No |
| `500` | Verification service temporarily unavailable | Yes (backoff) |

## Caveats

- **SEBI lists current registrations only.** A lapsed or cancelled SEBI registration reads `NOT_FOUND` — it can't be distinguished from never-registered.
- **`stock-broker` resolves against the equity register.** A broker registered only in a non-equity segment may read `NOT_FOUND`.
- **Frontend:** never expose your API key. Mint an access token (`at_`) via `POST /v1/token` and pass it as `x-api-key`.
