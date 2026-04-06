# Agency OS — SQL Query Reference

All queries work against `agency.db` (SQLite).  
Paste them into the **Dashboard → Database → Custom SQL Query** box, or run via any SQLite client.

---

## Schema

### `clients`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-increment primary key |
| `business_name` | TEXT | Client business name |
| `created_at` | TEXT | ISO timestamp when brief was submitted |
| `input_data` | TEXT | JSON blob — full client brief form fields |
| `outputs` | TEXT | JSON blob — all 7 agent outputs |

### `run_logs`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-increment primary key |
| `client_id` | INTEGER | Foreign key → clients.id |
| `started_at` | TEXT | ISO timestamp when crew run started |
| `finished_at` | TEXT | ISO timestamp when crew run finished |
| `status` | TEXT | `success`, `error`, or `running` |
| `error` | TEXT | Error message (only on failed runs) |
| `tokens_input` | INTEGER | Prompt/input tokens used (70% of total) |
| `tokens_output` | INTEGER | Completion/output tokens used (30% of total) |
| `tokens_total` | INTEGER | Total tokens across all 7 agents for this run |
| `cost_usd` | REAL | Actual or calibrated OpenAI cost in USD |
| `duration_secs` | INTEGER | Wall-clock seconds the full crew run took |

> **Token source:** LangChain `get_openai_callback()` when available. Falls back to a char-based estimate  
> calibrated against real OpenAI dashboard figures (6.39× multiplier, GPT-4o pricing: $2.50/1M input + $10.00/1M output).

---

## Clients

**All clients — overview**
```sql
SELECT id, business_name, created_at
FROM clients
ORDER BY created_at DESC
```

**Full input data for a specific client**
```sql
SELECT id, business_name, input_data
FROM clients
WHERE id = 1
```

**Check how much output data is stored per client**
```sql
SELECT id, business_name, length(outputs) AS output_bytes, created_at
FROM clients
ORDER BY output_bytes DESC
```

**Clients that have outputs saved**
```sql
SELECT id, business_name, length(outputs) AS output_size
FROM clients
WHERE outputs IS NOT NULL AND outputs != '{}'
ORDER BY output_size DESC
```

**Clients with NO outputs yet**
```sql
SELECT id, business_name, created_at
FROM clients
WHERE outputs IS NULL OR outputs = '{}'
```

**Search clients by name**
```sql
SELECT id, business_name, created_at
FROM clients
WHERE business_name LIKE '%Fit%'
```

---

## Inspect DB Schema

**List all tables**
```sql
SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name
```

**Full schema — all CREATE statements**
```sql
SELECT name, sql FROM sqlite_master WHERE type = 'table' ORDER BY name
```

**Column info for `clients`**
```sql
PRAGMA table_info(clients)
```

**Column info for `run_logs`**
```sql
PRAGMA table_info(run_logs)
```

**Check which columns exist (useful after migrations)**
```sql
SELECT name, type, dflt_value FROM pragma_table_info('run_logs')
```

---

## Run Logs

**All run logs — newest first**
```sql
SELECT * FROM run_logs ORDER BY id DESC
```

**Only successful runs**
```sql
SELECT * FROM run_logs WHERE status = 'success' ORDER BY started_at DESC
```

**Only failed runs**
```sql
SELECT * FROM run_logs WHERE status = 'error' ORDER BY started_at DESC
```

**Count runs by status**
```sql
SELECT status, COUNT(*) AS total
FROM run_logs
GROUP BY status
```

**Total number of runs**
```sql
SELECT COUNT(*) AS total_runs FROM run_logs
```

**Token and cost summary across all successful runs**
```sql
SELECT
    SUM(tokens_total)  AS total_tokens,
    SUM(tokens_input)  AS total_input_tokens,
    SUM(tokens_output) AS total_output_tokens,
    ROUND(SUM(cost_usd), 4) AS total_cost_usd,
    ROUND(AVG(cost_usd), 4) AS avg_cost_per_run
FROM run_logs
WHERE status IN ('success', 'complete')
```

**Cost and tokens per run with client name**
```sql
SELECT r.id, c.business_name,
       r.tokens_total, r.tokens_input, r.tokens_output,
       r.cost_usd, r.duration_secs, r.status
FROM run_logs r
JOIN clients c ON c.id = r.client_id
ORDER BY r.id DESC
```

**Runs with zero tokens (not yet estimated)**
```sql
SELECT r.id, c.business_name, r.status
FROM run_logs r
JOIN clients c ON c.id = r.client_id
WHERE r.tokens_total = 0
```

**Slowest runs by duration**
```sql
SELECT r.id, c.business_name, r.duration_secs, r.cost_usd
FROM run_logs r
JOIN clients c ON c.id = r.client_id
WHERE r.duration_secs > 0
ORDER BY r.duration_secs DESC
```

---

## Joins — Clients + Run Logs

**Full view — client name + run status**
```sql
SELECT c.id, c.business_name, c.created_at,
       r.status, r.started_at, r.finished_at, r.error
FROM clients c
LEFT JOIN run_logs r ON r.client_id = c.id
ORDER BY c.created_at DESC
```

**Clients with no run log yet**
```sql
SELECT c.id, c.business_name
FROM clients c
LEFT JOIN run_logs r ON r.client_id = c.id
WHERE r.id IS NULL
```

**Latest run per client**
```sql
SELECT c.id, c.business_name,
       r.status, r.started_at, r.finished_at,
       r.tokens_total, r.cost_usd, r.duration_secs
FROM clients c
LEFT JOIN run_logs r ON r.id = (
    SELECT id FROM run_logs
    WHERE client_id = c.id
    ORDER BY started_at DESC
    LIMIT 1
)
ORDER BY c.created_at DESC
```

**Success rate (percentage)**
```sql
SELECT
    ROUND(100.0 * SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) / COUNT(*), 1)
    AS success_rate_pct
FROM run_logs
```

---

## Maintenance

**Delete a client and their run logs**
```sql
DELETE FROM run_logs WHERE client_id = 1;
DELETE FROM clients WHERE id = 1;
```

**Reset auto-increment counter (after deleting all rows)**
```sql
DELETE FROM sqlite_sequence WHERE name = 'clients';
DELETE FROM sqlite_sequence WHERE name = 'run_logs';
```

**Wipe everything and start fresh**
```sql
DELETE FROM run_logs;
DELETE FROM clients;
DELETE FROM sqlite_sequence;
```

---

## SQLite CLI (Terminal)

Open the database directly from PowerShell:

```powershell
cd d:\LLM_OPS\ai-agency-mvp
sqlite3 agency.db
```

Useful SQLite shell commands:
```
.tables          -- list all tables
.schema          -- show CREATE statements
.mode column     -- pretty column output
.headers on      -- show column headers
.quit            -- exit
```
