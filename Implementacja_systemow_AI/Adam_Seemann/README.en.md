# AGPW – Ingest & API System for GPW (Warsaw Stock Exchange) Data

AGPW combines ingestion of GPW stock market data, local data analysis, Excel/CSV/JSON file classification, and a lightweight FastAPI-based API. The system uses SQLite and can run locally without an external database. Automated ingestion handles daily stock and index quote files, ticker and sector maps, and an additional module scrapes stock analyst recommendations.

## Status

- The API provides access to stock and index quotes, technical scoring with SMA/EMA averages, price and volume anomalies, and a text report for a given company.
- Ingestion handles Excel, CSV, and JSON files with GPW data, as well as PDF/XLSX financial reports parsed locally via LangGraph and Ollama.
- Agent modules perform technical and fundamental analysis, detect anomalies, calculate scores, and generate a short report.
- The API is monitored with Prometheus metrics and request logs; the container has a configured healthcheck.
- The SQLite database is initialized via SQL migrations (`data/migrations/`), and the API's connection is opened once at application startup (lifespan) and reused for every request.
- CI/CD runs code quality checks (ruff, mypy, bandit), tests, Docker image build, and optional automatic deployment via SSH.
- The React/Vite/TypeScript/Tailwind frontend MVP provides a company search and a dashboard with a chart, indicators, score, and report.
- Tests: **71 passed**.

## Features

### API (FastAPI)
- `GET /health` — simple liveness endpoint, returns `{"status": "ok"}`
- `GET /health/ready` — checks SQLite database availability (returns `503` when the database is unavailable)
- `GET /metrics` — Prometheus metrics (`agpw_http_requests_total`, `agpw_http_request_duration_seconds`)
- `GET /api/ticker-map` — list of tickers, names, sectors, and markets for the frontend search
- `GET /api/stocks/{ticker}` — daily quotes looked up by ticker or ISIN
- `GET /api/indices/{index_name}` — daily index quotes
- `GET /api/score/{ticker}` — technical indicators (SMA and EMA for periods 12, 26, 50, and 200; RSI, ATR, MACD, Bollinger bands, and A/D), price and volume anomalies, and a 0–100 score
- `GET /api/report/{ticker}` — text technical report for a company

Stock, index, scoring, and report endpoints accept optional `start_date` and `end_date` parameters in `YYYY-MM-DD` format. They return `404` when an instrument has no data, and `400` for an inverted date range. The report includes technical score and anomalies; the fundamental score is marked as unavailable until fundamental data is stored in the database. For the local frontend, the API allows CORS requests from `http://localhost:5173`.

Stock, index, scoring, and report endpoints accept optional `start_date` and `end_date` parameters in `YYYY-MM-DD` format. They return `404` when an instrument has no data, and `400` for an inverted date range. The report includes technical score and anomalies; the fundamental score is marked as unavailable until fundamental data is stored in the database.

Example calls:

```text
GET /api/stocks/AGPW?start_date=2026-01-01&end_date=2026-01-31
GET /api/indices/WIG20
GET /api/score/AGPW?start_date=2026-01-01&end_date=2026-01-31
GET /api/report/AGPW?start_date=2026-01-01&end_date=2026-01-31
```

Example response fragment for `GET /api/score/AGPW`:

```json
{
	"ticker": "AGPW",
	"analysis": {
		"latest_close": 119.5,
		"sma_12": 116.75,
		"sma_26": 113.25,
		"sma_50": null,
		"sma_200": null,
		"ema_12": 116.7541,
		"ema_26": 113.5607,
		"ema_50": null,
		"ema_200": null,
		"rsi_14": 100.0,
		"atr_14": 4.0,
		"ad": 0.0
	}
}
```

The `sma_12`, `sma_26`, `sma_50`, `sma_200` and `ema_12`, `ema_26`, `ema_50`, `ema_200` fields are the current values of the moving averages. SMA and EMA return `null` when the number of quotes is smaller than their period length. The `ad` field represents the current value of the accumulation/distribution line. It requires `high`, `low`, `close`, and `volume` data; when volume is unavailable, the API returns `null`.

### Data analysis
- technical indicators: SMA, EMA, MACD, RSI, ATR, Bollinger bands, OBV, A/D, and the stochastic oscillator
- detection of unusual daily price changes using z-score
- detection of volume spikes and drops, and price/volume divergences
- fundamental models: income statement, balance sheet, cash flow, and aggregated financial metrics
- technical and fundamental health score on a 0–100 scale
- detection of fundamental warnings, including negative net income, high debt, and negative FCF
- generation of a text report for a company

### GPW data ingestion
- reading Excel (`.xlsx`, `.xls`), CSV (`.csv`, with auto-detection of separator and Windows-1250/ISO-8859-2 encoding), and JSON (`.json`) files via pandas
- structural validation shared across all formats: rejecting files without headers, with duplicate columns, or unnamed columns, and removing fully empty rows
- heuristic classification with an optional local Ollama/Phi-3 LLM as fallback
- column validation and mapping
- saving stock and index quotes to SQLite (`data/agpw.db`)
- saving ticker maps (`tickers`) and sector data (`sector_companies`, `sector_index_map`) with upsert by logical key
- fetching stock analyst recommendations from biznesradar.pl and saving them to SQLite (`recommendations`)
- moving successfully processed files to `data/incoming/loaded/`
- moving unhandled or invalid files to `data/incoming/unknown/`
- logging to console and to a rotated `logs/ingest.log` file

### Monitoring
- Prometheus metrics at `GET /metrics` (`agpw_http_requests_total`, `agpw_http_request_duration_seconds`)
- logging of every API request (method, path, status, duration) to console and to a rotated `logs/api.log` file
- Docker container healthcheck (`docker/Dockerfile`, `docker/docker-compose.yml`) polling `GET /health`
- readiness endpoint `GET /health/ready` verifying the SQLite database connection

## Running locally

### Requirements
- Python 3.11+
- pip
- dependencies from `requirements.txt`
- Ollama with the `phi3` and `qwen2.5:7b` models for local classification and financial report extraction

### Installation
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
ollama pull phi3
ollama pull qwen2.5:7b
# pytest and httpx are needed to run the tests
pip install pytest httpx
# ruff, mypy, and bandit for code quality checks
pip install -r requirements-dev.txt
```

### Running the API
```bash
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### React frontend

The frontend MVP is located in the `frontend/` directory. After starting the API, run it in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173` and uses a Vite proxy to the API at `http://localhost:8000`. A production image can be built with `docker build -t agpw-frontend frontend`.

### Running with Docker
```bash
docker build -f docker/Dockerfile -t agpw .
docker run -p 8000:8000 agpw
```

The Docker image runs the API. The `data/` and `logs/` directories can be mounted as volumes to keep the database and logs outside the container:

```bash
docker run -p 8000:8000 -v "${PWD}/data:/app/data" -v "${PWD}/logs:/app/logs" agpw
```

Alternatively, `docker/docker-compose.yml` runs the API together with local Ollama (for LLM classification) and has a configured healthcheck and `restart: unless-stopped`:

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

### Ingesting data files and financial reports

Files placed in `data/incoming/` are processed after manually running the command:

1. File type classification
2. Data validation
3. Saving to SQLite
4. Moving the file to `data/incoming/loaded/` or `data/incoming/unknown/`

**Supported GPW data file types:**

| Type | Required columns |
|-----|-----------------|
| STOCK_DAILY | `isin` and `Kurs zamknięcia` or `date`, `open`, `high`, `low`, `close`, `volume` |
| INDEX_DAILY | `nazwa` and `Kurs zamknięcia` or `date`, `open`, `high`, `low`, `close` |
| TICKER_MAP | `ticker`, `name` |
| SECTOR_COMPOSITION | `sector`, `ticker` |
| SECTOR_INDEX_MAP | `sector`, `index_name` |

A financial report in `.pdf` format, as well as an `.xlsx`/`.xls` file that does not match the GPW formats above, is routed to the LangGraph graph. Long documents are split into chunks of at most 24,000 characters while preserving PDF page markers. The local `qwen2.5:7b` Ollama model extracts metrics, period, company, and value source from each chunk, and the results are merged with deduplication of metrics by period and higher confidence. After validation, the data is stored in the `financial_reports` and `financial_metrics` tables; a successfully processed file is moved to `data/incoming/loaded/`, and a file with an error to `data/incoming/unknown/`.

The PDF must contain a text layer. Reports that are scans only require OCR before ingestion.

**Running the ingest:**
```bash
python -m agent.ingest.run_ingest --dir data/incoming
```

### Analyst recommendations (biznesradar.pl)

The `agent/ingest/scrape_recommendations.py` module fetches the stock recommendations table from
[biznesradar.pl/rekomendacje](https://www.biznesradar.pl/rekomendacje/) and saves it to the `recommendations` table
in SQLite (upsert by ticker + publication date + author key).

```bash
python -m agent.ingest.scrape_recommendations
```

Saved fields: `ticker`, `company_name`, `recommendation` (recommendation type), `target_price`,
`current_price`, `potential_pct` (potential %), `price_at_issue` (price on the issue date),
`published_at`, `author`, `source_url`.

### Sample data

For local development, 40 repeatable quotes can be created for the `AGPW` ticker:

```bash
python scripts/seed_sample_data.py
```

The script is idempotent for the same dates and stores data in `data/agpw.db`. A custom database can be specified with the `--db` parameter.

Additional helper scripts in `scripts/`:
- `create_sample_excel.py` — generates a sample Excel file for ingest testing
- `print_excel_headers.py` — prints column headers from an Excel file
- `clean_db_duplicates.py` — removes duplicate records from the SQLite database

## Tests

Tests cover reading and validating Excel/CSV/JSON files, classification, ingestion of stocks, indices, ticker maps and sector data, recommendation scraping, saving and updating data in SQLite, handling of unknown files, API endpoints (including health/metrics), technical and fundamental analysis models, price and volume anomaly detection, and the scoring and reporting agents.

Running the tests:
```bash
python -m pytest -v
```

Last verified result: `71 passed`.

### Code quality

Tool configuration is located in `pyproject.toml`. Running locally:
```bash
ruff check .
mypy agent api data scripts
bandit -c pyproject.toml -r agent api data scripts
```
All three tools are also run in CI (the `lint` job) before tests and the image build.

## Project structure

```
.
├── api/                      # FastAPI application (endpoints, lifespan, middleware, metrics)
├── agent/                    # Agents, models, and ingestion logic
│   ├── ingest/               # Reading, classification, ingestion, and recommendation scraping
│   └── models/               # Fundamental models and technical indicators
├── data/                     # SQLite database + migrations + input files
│   ├── agpw.db               # created when the database is initialized
│   ├── migrations/           # SQL migrations (NNNN_description.sql), applied in order at startup
│   ├── incoming/
│   ├── loaded/
│   └── unknown/
├── docker/                   # Dockerfile and docker-compose
├── logs/                     # ingest logs (ingest.log) and API logs (api.log)
├── tests/                    # Automated tests
├── scripts/                  # Helper scripts, including data seeding
├── .github/workflows/        # CI/CD
├── pyproject.toml            # ruff/mypy/bandit configuration
├── requirements.txt          # Python dependencies (runtime)
└── requirements-dev.txt      # Development dependencies (ruff, mypy, bandit)
```

**Key modules:**
- `data/db.py` — SQLite connection and CRUD operations, database initialization via migrations
- `data/migrator.py` — SQL migration runner (Goose-style): applies files from `data/migrations/` in order, tracks applied versions in the `schema_migrations` table
- `api/server.py` — FastAPI endpoints
- `api/lifespan.py` — runs migrations and opens the shared SQLite connection at application startup
- `api/database.py` — `DatabaseSession` (connection + lock) and the `get_db_session` dependency injected into endpoints
- `api/middlewares.py` — CORS and the request-logging/Prometheus middleware
- `api/metrics.py` — Prometheus metric definitions (`agpw_http_requests_total`, `agpw_http_request_duration_seconds`)
- `agent/ingest/file_router.py` — main ingestion orchestrator
- `agent/ingest/file_reader.py` — reading and validating Excel/CSV/JSON files
- `agent/ingest/file_llm_classifier.py` — file classification
- `agent/ingest/ingest_stocks_daily.py` — stock data ingestion
- `agent/ingest/ingest_indexes_daily.py` — index data ingestion
- `agent/ingest/ingest_ticker_map.py` / `ingest_sector_composition.py` / `ingest_sector_index_map.py` — ingestion of ticker maps and sector data
- `agent/ingest/scrape_recommendations.py` — scraping analyst recommendations from biznesradar.pl
- `agent/agents.py` — analysis, anomalies, scoring, and reporting
- `agent/models/technical.py` — technical analysis indicators
- `agent/models/volume_anomalies.py` — volume anomaly detection
- `agent/models/fundamental.py` — fundamental data models

## CI/CD

The `.github/workflows/ci-cd.yml` workflow runs on pushes and pull requests to the `main` branch and includes three jobs:

1. **`lint`** — `ruff check .`, `mypy agent api data scripts`, `bandit -c pyproject.toml -r agent api data scripts`
2. **`test`** — `pytest -q`
3. **`build-and-deploy`** (only for pushes to `main`, after `lint` and `test` succeed) — builds the Docker image, publishes it to the GitHub Container Registry, and then attempts automatic deployment

### Deployment automation

The deployment step connects to the target server via SSH and runs `docker compose pull && docker compose up -d`
based on the image published to GHCR. If the required secrets are not configured, the step is automatically
skipped (the pipeline does not fail). Required repository secrets:

| Secret | Description |
|---|---|
| `DEPLOY_HOST` | Address/hostname of the target server |
| `DEPLOY_USER` | SSH user |
| `DEPLOY_SSH_KEY` | Private SSH key (without a passphrase) |
| `DEPLOY_PATH` | Path on the server with the cloned repository / the `docker/docker-compose.yml` file |

On the target server, the `AGPW_IMAGE` environment variable (e.g. in an `.env` file next to `docker-compose.yml`) should
point to the published image, e.g. `ghcr.io/<owner>/agpw:latest`.

---

**Last updated:** 2026-09-01

## Planned steps - "wishlist"

1. Identifying support and resistance zones
