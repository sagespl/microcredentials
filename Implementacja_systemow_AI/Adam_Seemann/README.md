# AGPW – System Ingestu i API dla danych GPW

AGPW łączy ingest danych giełdowych z GPW, lokalną analizę danych, klasyfikację plików Excel/CSV/JSON oraz lekkie API oparte na FastAPI. System korzysta z SQLite i może działać lokalnie bez zewnętrznej bazy danych. Automatyczny ingest obsługuje pliki dziennych notowań akcji i indeksów, mapy tickerów i sektorów, a dodatkowy moduł scrapuje rekomendacje analityków giełdowych.

## Status

- API udostępnia odczyt notowań akcji i indeksów, scoring techniczny ze średnimi SMA/EMA, anomaliami cenowymi i wolumenowymi oraz tekstowy raport dla spółki.
- Ingest obsługuje pliki Excel, CSV i JSON z danymi GPW oraz raporty finansowe PDF/XLSX analizowane lokalnie przez LangGraph i Ollama.
- Moduły agentów wykonują analizę techniczną i fundamentalną, wykrywają anomalie, wyliczają oceny oraz generują krótki raport.
- API jest monitorowane metrykami Prometheusa i logami żądań; kontener ma skonfigurowany healthcheck.
- Baza SQLite jest inicjalizowana migracjami SQL (`data/migrations/`), a połączenie API jest otwierane raz przy starcie aplikacji (lifespan) i reużywane dla każdego żądania.
- CI/CD uruchamia kontrolę jakości kodu (ruff, mypy, bandit), testy, build obrazu Dockera oraz opcjonalne automatyczne wdrożenie przez SSH.
- Frontend MVP w React, Vite, TypeScript i Tailwind zapewnia wyszukiwarkę spółek oraz dashboard z wykresem, wskaźnikami, oceną i raportem.
- Testy: **71 passed**.

## Funkcje

### API (FastAPI)
- `GET /health` — prosty endpoint żywotności, zwraca `{"status": "ok"}`
- `GET /health/ready` — sprawdza dostępność bazy SQLite (zwraca `503`, gdy baza jest niedostępna)
- `GET /metrics` — metryki Prometheusa (`agpw_http_requests_total`, `agpw_http_request_duration_seconds`)
- `GET /api/ticker-map` — lista tickerów, nazw, sektorów i rynków dla wyszukiwarki frontendu
- `GET /api/stocks/{ticker}` — notowania dzienne wyszukiwane po tickerze lub ISIN
- `GET /api/indices/{index_name}` — notowania dzienne indeksu
- `GET /api/score/{ticker}` — wskaźniki techniczne (SMA i EMA dla okresów 12, 26, 50 i 200; RSI, ATR, MACD, wstęgi Bollingera i A/D), anomalie cenowe i wolumenowe oraz ocena 0–100
- `GET /api/report/{ticker}` — tekstowy raport techniczny spółki

Endpointy akcji, indeksów, scoringu i raportu przyjmują opcjonalne parametry `start_date` oraz `end_date` w formacie `YYYY-MM-DD`. Zwracają `404`, gdy instrument nie ma danych, oraz `400` dla odwróconego zakresu dat. Raport zawiera ocenę techniczną i anomalie; ocena fundamentalna jest oznaczana jako niedostępna, dopóki dane fundamentalne nie są zapisywane w bazie. Dla lokalnego frontendu API dopuszcza żądania CORS z `http://localhost:5173`.

Przykładowe wywołania:

```text
GET /api/stocks/AGPW?start_date=2026-01-01&end_date=2026-01-31
GET /api/indices/WIG20
GET /api/score/AGPW?start_date=2026-01-01&end_date=2026-01-31
GET /api/report/AGPW?start_date=2026-01-01&end_date=2026-01-31
```

Przykładowy fragment odpowiedzi `GET /api/score/AGPW`:

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

Pola `sma_12`, `sma_26`, `sma_50`, `sma_200` oraz `ema_12`, `ema_26`, `ema_50`, `ema_200` są bieżącymi wartościami średnich kroczących. SMA i EMA zwracają `null`, gdy liczba notowań jest mniejsza niż długość ich okresu. Pole `ad` oznacza bieżącą wartość linii akumulacji/dystrybucji. Wymaga danych `high`, `low`, `close` i `volume`; gdy wolumen nie jest dostępny, API zwraca `null`.

### Analiza danych
- wskaźniki techniczne: SMA, EMA, MACD, RSI, ATR, wstęgi Bollingera, OBV, A/D i oscylator stochastyczny
- wykrywanie nietypowych dziennych zmian ceny za pomocą z-score
- wykrywanie skoków i spadków wolumenu oraz rozbieżności ceny i wolumenu
- modele fundamentalne: rachunek wyników, bilans, przepływy pieniężne i zagregowane metryki finansowe
- ocena kondycji technicznej i fundamentalnej w skali 0–100
- wykrywanie ostrzeżeń fundamentalnych, m.in. ujemnego wyniku, wysokiego zadłużenia i ujemnego FCF
- generowanie tekstowego raportu dla spółki

### Ingest danych GPW
- odczyt plików Excel (`.xlsx`, `.xls`), CSV (`.csv`, z auto-wykrywaniem separatora i kodowania Windows-1250/ISO-8859-2) oraz JSON (`.json`) przez pandas
- walidacja strukturalna wspólna dla wszystkich formatów: odrzucanie plików bez nagłówków, z duplikatami kolumn lub kolumnami bez nazwy oraz usuwanie w pełni pustych wierszy
- klasyfikacja heurystyczna z opcjonalnym lokalnym LLM Ollama/Phi-3 jako fallbackiem
- walidacja i mapowanie kolumn
- zapis notowań akcji i indeksów do SQLite (`data/agpw.db`)
- zapis map tickerów (`tickers`) oraz danych sektorowych (`sector_companies`, `sector_index_map`) z upsertem po kluczu logicznym
- pobieranie rekomendacji analityków giełdowych ze strony biznesradar.pl i zapis do SQLite (`recommendations`)
- przenoszenie poprawnie przetworzonych plików do `data/incoming/loaded/`
- przenoszenie nieobsłużonych lub błędnych plików do `data/incoming/unknown/`
- logowanie do konsoli i rotowanego pliku `logs/ingest.log`

### Monitoring
- metryki Prometheusa pod `GET /metrics` (`agpw_http_requests_total`, `agpw_http_request_duration_seconds`)
- logowanie każdego żądania API (metoda, ścieżka, status, czas trwania) do konsoli i rotowanego pliku `logs/api.log`
- healthcheck kontenera Dockera (`docker/Dockerfile`, `docker/docker-compose.yml`) odpytujący `GET /health`
- endpoint gotowości `GET /health/ready` weryfikujący połączenie z bazą SQLite

## Uruchamianie lokalne

### Wymagania
- Python 3.11+
- pip
- zależności z `requirements.txt`
- Ollama z modelami `phi3` oraz `qwen2.5:7b` do lokalnej klasyfikacji i ekstrakcji raportów finansowych

### Instalacja
```bash
python -m venv .venv
source .venv/bin/activate  # lub .venv\Scripts\Activate.ps1 na Windows
pip install -r requirements.txt
ollama pull phi3
ollama pull qwen2.5:7b
# pytest i httpx są potrzebne do uruchomienia testów
pip install pytest httpx
# ruff, mypy i bandit do kontroli jakości kodu
pip install -r requirements-dev.txt
```

### Uruchomienie API
```bash
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### Frontend React

Frontend MVP znajduje się w katalogu `frontend/`. Po uruchomieniu API uruchom go w drugim terminalu:

```bash
cd frontend
npm install
npm run dev
```

Aplikacja będzie dostępna pod `http://localhost:5173` i korzysta z proxy Vite do API `http://localhost:8000`. Produkcyjny obraz można zbudować poleceniem `docker build -t agpw-frontend frontend`.

### Uruchamianie z Dockerem
```bash
docker build -f docker/Dockerfile -t agpw .
docker run -p 8000:8000 agpw
```

Obraz Docker uruchamia API. Pliki `data/` i `logs/` można podłączyć jako wolumeny, aby zachować bazę i logi poza kontenerem:

```bash
docker run -p 8000:8000 -v "${PWD}/data:/app/data" -v "${PWD}/logs:/app/logs" agpw
```

Alternatywnie, `docker/docker-compose.yml` uruchamia API razem z lokalnym Ollama (dla klasyfikacji LLM) i ma skonfigurowany healthcheck oraz `restart: unless-stopped`:

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

### Ingest plików danych i raportów finansowych

Pliki umieszczone w `data/incoming/` są przetwarzane po ręcznym uruchomieniu polecenia:

1. Klasyfikacja typu pliku
2. Walidacja danych
3. Zapis do SQLite
4. Przeniesienie pliku do `data/incoming/loaded/` albo `data/incoming/unknown/`

**Obsługiwane typy plików danych GPW:**

| Typ | Wymagane kolumny |
|-----|-----------------|
| STOCK_DAILY | `isin` i `Kurs zamknięcia` lub `date`, `open`, `high`, `low`, `close`, `volume` |
| INDEX_DAILY | `nazwa` i `Kurs zamknięcia` lub `date`, `open`, `high`, `low`, `close` |
| TICKER_MAP | `ticker`, `name` |
| SECTOR_COMPOSITION | `sector`, `ticker` |
| SECTOR_INDEX_MAP | `sector`, `index_name` |

Raport finansowy w formacie `.pdf`, a także plik `.xlsx`/`.xls`, który nie pasuje do powyższych formatów GPW, jest kierowany do grafu LangGraph. Długie dokumenty są dzielone na fragmenty po maksymalnie 24 000 znaków z zachowaniem oznaczeń stron PDF. Lokalny model Ollama `qwen2.5:7b` wydobywa metryki, okres, spółkę i źródło wartości z każdego fragmentu, a wyniki są scalane z deduplikacją metryk według okresu i wyższego poziomu pewności. Po walidacji dane trafiają do tabel `financial_reports` i `financial_metrics`; poprawnie przetworzony plik jest przenoszony do `data/incoming/loaded/`, a plik z błędem do `data/incoming/unknown/`.

PDF musi zawierać warstwę tekstową. Raporty będące wyłącznie skanami wymagają OCR przed ingesem.

**Uruchomienie ingestu:**
```bash
python -m agent.ingest.run_ingest --dir data/incoming
```

### Rekomendacje analityków (biznesradar.pl)

Moduł `agent/ingest/scrape_recommendations.py` pobiera tabelę rekomendacji giełdowych ze strony
[biznesradar.pl/rekomendacje](https://www.biznesradar.pl/rekomendacje/) i zapisuje ją do tabeli `recommendations`
w SQLite (upsert po kluczu ticker + data upublicznienia + autor).

```bash
python -m agent.ingest.scrape_recommendations
```

Zapisywane pola: `ticker`, `company_name`, `recommendation` (rodzaj rekomendacji), `target_price` (cena docelowa),
`current_price` (kurs aktualny), `potential_pct` (CD/K, potencjał %), `price_at_issue` (kurs z dnia wydania),
`published_at`, `author`, `source_url`.

### Dane przykładowe

Do lokalnego developmentu można utworzyć 40 powtarzalnych notowań dla tickeru `AGPW`:

```bash
python scripts/seed_sample_data.py
```

Skrypt jest idempotentny dla tych samych dat i zapisuje dane w `data/agpw.db`. Własną bazę można wskazać parametrem `--db`.

Dodatkowe skrypty pomocnicze w `scripts/`:
- `create_sample_excel.py` — generuje przykładowy plik Excel do testów ingestu
- `print_excel_headers.py` — wypisuje nagłówki kolumn z pliku Excel
- `clean_db_duplicates.py` — usuwa zduplikowane rekordy z bazy SQLite

## Testy

Testy pokrywają odczyt i walidację plików Excel/CSV/JSON, klasyfikację, ingest akcji, indeksów, map tickerów i danych sektorowych, scraping rekomendacji, zapis i aktualizację danych w SQLite, obsługę nieznanych plików, endpointy API (w tym health/metrics), modele analizy technicznej i fundamentalnej, wykrywanie anomalii cenowych i wolumenowych oraz agentów oceny i raportowania.

Uruchomienie testów:
```bash
python -m pytest -v
```

Ostatni zweryfikowany wynik: `71 passed`.

### Jakość kodu

Konfiguracja narzędzi znajduje się w `pyproject.toml`. Uruchomienie lokalnie:
```bash
ruff check .
mypy agent api data scripts
bandit -c pyproject.toml -r agent api data scripts
```
Wszystkie trzy narzędzia są również uruchamiane w CI (zadanie `lint`) przed testami i budowaniem obrazu.

## Struktura projektu

```
.
├── api/                      # FastAPI aplikacja (endpointy, lifespan, middleware, metryki)
├── agent/                    # Agenci, modele i logika ingestu
│   ├── ingest/               # Odczyt, klasyfikacja, ingest i scraping rekomendacji
│   └── models/               # Modele fundamentalne i wskaźniki techniczne
├── data/                     # Baza SQLite + migracje + pliki wejściowe
│   ├── agpw.db               # tworzona przy inicjalizacji bazy
│   ├── migrations/           # migracje SQL (NNNN_opis.sql), aplikowane po kolei przy starcie
│   ├── incoming/
│   ├── loaded/
│   └── unknown/
├── docker/                   # Dockerfile i docker-compose
├── logs/                     # logi ingestu (ingest.log) i API (api.log)
├── tests/                    # Testy automatyczne
├── scripts/                  # Skrypty pomocnicze, w tym seed danych
├── .github/workflows/        # CI/CD
├── pyproject.toml            # konfiguracja ruff/mypy/bandit
├── requirements.txt          # Zależności Python (runtime)
└── requirements-dev.txt      # Zależności deweloperskie (ruff, mypy, bandit)
```

**Kluczowe moduły:**
- `data/db.py` — połączenie SQLite i operacje CRUD, inicjalizacja bazy przez migracje
- `data/migrator.py` — runner migracji SQL (styl Goose): stosuje kolejno pliki z `data/migrations/`, śledzi zaaplikowane wersje w tabeli `schema_migrations`
- `api/server.py` — endpointy FastAPI
- `api/lifespan.py` — uruchamia migracje i otwiera współdzielone połączenie SQLite przy starcie aplikacji
- `api/database.py` — `DatabaseSession` (połączenie + blokada) i zależność `get_db_session` wstrzykiwana do endpointów
- `api/middlewares.py` — CORS oraz middleware logujące żądania i zasilające metryki Prometheusa
- `api/metrics.py` — definicje metryk Prometheusa (`agpw_http_requests_total`, `agpw_http_request_duration_seconds`)
- `agent/ingest/file_router.py` — główny orkestrator ingestu
- `agent/ingest/file_reader.py` — odczyt i walidacja plików Excel/CSV/JSON
- `agent/ingest/file_llm_classifier.py` — klasyfikacja plików
- `agent/ingest/ingest_stocks_daily.py` — ingest danych akcji
- `agent/ingest/ingest_indexes_daily.py` — ingest danych indeksów
- `agent/ingest/ingest_ticker_map.py` / `ingest_sector_composition.py` / `ingest_sector_index_map.py` — ingest map tickerów i danych sektorowych
- `agent/ingest/scrape_recommendations.py` — scraping rekomendacji analityków z biznesradar.pl
- `agent/agents.py` — analiza, anomalie, scoring i raportowanie
- `agent/models/technical.py` — wskaźniki analizy technicznej
- `agent/models/volume_anomalies.py` — wykrywanie anomalii wolumenu
- `agent/models/fundamental.py` — modele danych fundamentalnych

## CI/CD

Workflow `.github/workflows/ci-cd.yml` uruchamia się dla pushy i pull requestów do gałęzi `main` i obejmuje trzy zadania:

1. **`lint`** — `ruff check .`, `mypy agent api data scripts`, `bandit -c pyproject.toml -r agent api data scripts`
2. **`test`** — `pytest -q`
3. **`build-and-deploy`** (tylko dla push do `main`, po powodzeniu `lint` i `test`) — buduje obraz Dockera, publikuje go do GitHub Container Registry, a następnie próbuje automatycznego wdrożenia

### Automatyzacja wdrożenia

Krok wdrożenia łączy się z serwerem docelowym przez SSH i uruchamia `docker compose pull && docker compose up -d`
na podstawie obrazu opublikowanego w GHCR. Jeśli wymagane sekrety nie są skonfigurowane, krok jest automatycznie
pomijany (pipeline nie kończy się błędem). Wymagane sekrety repozytorium:

| Sekret | Opis |
|---|---|
| `DEPLOY_HOST` | Adres/hostname serwera docelowego |
| `DEPLOY_USER` | Użytkownik SSH |
| `DEPLOY_SSH_KEY` | Prywatny klucz SSH (bez hasła) |
| `DEPLOY_PATH` | Ścieżka na serwerze z sklonowanym repozytorium / plikiem `docker/docker-compose.yml` |

Na serwerze docelowym zmienna środowiskowa `AGPW_IMAGE` (np. w pliku `.env` obok `docker-compose.yml`) powinna
wskazywać opublikowany obraz, np. `ghcr.io/<owner>/agpw:latest`.

---

**Ostatnia aktualizacja:** 2026-09-01

## Planowane kroki - "lista życzeń"

1. Wyznaczenie stref wsparcia i oporu
