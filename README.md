# market-pulse

> An async, LLM-powered financial market intelligence CLI that aggregates multi-source data, detects anomalies, and generates analyst-grade reports — all from your terminal.

```
pulse report AAPL --depth full
```

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AAPL — Full Analysis Report          2024-01-15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Summary        Strong fundamentals with services
                 segment accelerating. Hardware cycle
                 headwinds offset by margin expansion.

  Bull Case  ▸  Services revenue CAGR 15%+
             ▸  India market penetration early innings
             ▸  Vision Pro optionality

  Bear Case  ▸  China regulatory + demand risk
             ▸  Peak smartphone saturation
             ▸  Valuation premium vs. growth rate

  Key Risks  ⚠  Antitrust: App Store fee litigation
             ⚠  Macro: Consumer discretionary pressure
             ⚠  FX: Strong USD compresses int'l revenue

  Target Range   $178 – $224   (current: $189.42)
  RSI            58.4  ·  Bollinger: mid-band
  Sentiment      0.71 / 1.0  (152 news sources)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Why

Tracking a stock requires juggling price charts, SEC filings, news feeds, earnings transcripts, Reddit sentiment, and technical indicators across a dozen different tabs. `market-pulse` collapses all of it into a single terminal-native tool:

- **5 data sources fetched concurrently** via Python 3.11+ `asyncio.TaskGroup`
- **Structured AI analysis** via Anthropic Claude tool use — guaranteed JSON output, no prompt hacking
- **Columnar analytics** with DuckDB + Polars — no database server required
- **Rich terminal UI** with live dashboards, tables, and progress indicators
- **Alert engine** with custom condition DSL and multi-channel notifications

---

## Features

| Command | Description |
|---|---|
| `pulse watch` | Live terminal dashboard — prices, sentiment, signals, auto-refreshing |
| `pulse report` | Full AI-generated investment analysis (quick / standard / full depth) |
| `pulse scan` | Scan a sector for active signals (RSI oversold, earnings catalyst, etc.) |
| `pulse compare` | Side-by-side peer comparison — fundamentals, growth, technicals |
| `pulse alert` | Set conditional alerts with a human-readable DSL |

---

## Data Sources

Data is fetched from **5 sources simultaneously** using `asyncio.TaskGroup`. Optional sources fail gracefully — the pipeline continues with available data.

| Source | Data | Library |
|---|---|---|
| Yahoo Finance | Price, OHLCV, fundamentals | `yfinance` |
| Alpha Vantage | Technical indicators, earnings | REST API |
| NewsAPI | News headlines for sentiment | REST API |
| SEC EDGAR | Latest 10-K / 10-Q filings | REST API |
| Reddit | Retail sentiment, mention count | `praw` |

---

## Analysis Engine

**Technical** — SMA (20/50/200), EMA, RSI, MACD, Bollinger Bands, volume spike detection. Implemented as pure Polars expressions — no loops, vectorized operations.

**Fundamental** — P/E, EV/EBITDA, revenue growth YoY, gross margin, free cash flow, simplified DCF estimate, EPS surprise tracking.

**Sentiment** — VADER applied to news headlines weighted by source recency. Reddit mention velocity as a secondary signal. Blended into a single −1.0 to 1.0 score.

**Anomaly Detection** — Z-score and IQR-based outlier detection on both price and volume. Flags abnormal moves for manual review.

**Peer Comparison** — Relative strength vs. sector peers. Ranks the target stock across multiple metrics.

---

## AI Layer

All AI-generated analysis uses **Claude's tool use API** — the model must call a structured tool with typed arguments rather than returning free-form text. This eliminates parsing fragility and guarantees a consistent output schema on every call.

```python
# Claude is forced to call generate_analysis() with typed arguments.
# No text extraction. No regex. Schema validated by Pydantic v2.
```

The AI layer handles:
- Investment analysis (bull/bear case, risks, price target range)
- SEC filing summarization — 10-K / 10-Q condensed to key takeaways
- News signal classification — identifies catalysts from headline clusters

---

## Stack

```
Python 3.12+      Language
uv                Package manager
Pydantic v2       Data validation & settings
DuckDB            Local analytical database (time-series, no server)
Polars            Columnar data processing
asyncio           Concurrent data fetching (TaskGroup)
Anthropic         LLM analysis via Claude tool use
Typer             CLI framework
Rich              Terminal UI (tables, live dashboards, progress)
APScheduler       Alert polling & watch mode scheduling
diskcache         Persistent API response caching
VADER             Rule-based sentiment scoring
weasyprint        Markdown → PDF export
Ruff              Linter
mypy (strict)     Type checker
pytest-asyncio    Async test runner
respx             HTTP mocking for tests
```

---

## Requirements

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed
- API keys (see Configuration)

---

## Installation

```bash
git clone https://github.com/boranesn/market-pulse.git
cd market-pulse

# Install dependencies
uv sync

# Copy and fill in your API keys
cp .env.example .env
```

---

## Configuration

```bash
# .env

ANTHROPIC_API_KEY=sk-ant-...        # Required — Claude analysis
ALPHA_VANTAGE_API_KEY=...           # Required — technical indicators
NEWS_API_KEY=...                    # Optional — sentiment (falls back gracefully)
REDDIT_CLIENT_ID=...                # Optional — Reddit sentiment
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=market-pulse/1.0

# Alert notifications (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@example.com
SMTP_PASSWORD=...
```

---

## Usage

### Live Watch Dashboard

```bash
uv run pulse watch AAPL MSFT NVDA
uv run pulse watch TSLA --interval 30   # Refresh every 30 seconds
```

```
┌──────────────────────────────────────────────────┐
│  market-pulse  ·  Live Watch  ·  14:32:07        │
├──────┬──────────┬─────────┬────────┬─────────────┤
│ TICK │ PRICE    │ CHG     │ SENT   │ SIGNAL      │
├──────┼──────────┼─────────┼────────┼─────────────┤
│ AAPL │  189.42  │ +1.2%   │  0.71  │ RSI neutral │
│ MSFT │  415.20  │ +0.3%   │  0.65  │ Above SMA50 │
│ NVDA │  875.10  │ -0.4%   │  0.88  │ Vol spike ⚠ │
└──────┴──────────┴─────────┴────────┴─────────────┘
  Refreshing in 58s  ·  q to quit
```

### Investment Report

```bash
uv run pulse report AAPL                    # Standard depth
uv run pulse report TSLA --depth full       # Full AI analysis
uv run pulse report NVDA --format pdf       # Export as PDF
uv run pulse report MSFT --format markdown  # Export as Markdown
```

### Sector Scan

```bash
uv run pulse scan --sector semiconductor --signal "rsi_oversold"
uv run pulse scan --sector fintech --signal "earnings_beat"
```

### Peer Comparison

```bash
uv run pulse compare AMZN GOOG META --metric revenue_growth
uv run pulse compare AAPL MSFT --years 3
```

### Alerts

```bash
# Add an alert
uv run pulse alert add NVDA \
  --condition "price > 200-day-MA" \
  --notify slack

# Condition DSL examples
"price > 900"
"rsi < 30"
"sentiment > 0.8"
"price > 200-day-MA"
"volume > 2x-avg"

# List active alerts
uv run pulse alert list

# Remove an alert
uv run pulse alert remove <id>

# Start alert polling daemon
uv run pulse alert daemon
```

---

## Architecture

```
                        ┌─────────────────────────┐
                        │       CLI (Typer)        │
                        └────────────┬────────────┘
                                     │
                        ┌────────────▼────────────┐
                        │    Data Aggregator      │
                        │   asyncio.TaskGroup     │
                        └──┬──┬──┬──┬──┬──────────┘
                           │  │  │  │  │
              ┌────────────┘  │  │  │  └────────────┐
              │               │  │  │               │
           Yahoo           Alpha  News   SEC       Reddit
          Finance         Vantage  API  EDGAR       PRAW
              │               │  │  │               │
              └───────────────┴──┴──┴───────────────┘
                                     │
                        ┌────────────▼────────────┐
                        │      Normalizer          │
                        │   → MarketSnapshot       │
                        └────────────┬────────────┘
                                     │
               ┌──────────┬──────────┼──────────┬──────────┐
               │          │          │          │          │
          Technical  Fundamental Sentiment  Anomaly    Peer
          Analysis    Analysis   Scoring   Detection  Compare
               │          │          │          │          │
               └──────────┴──────────┼──────────┴──────────┘
                                     │
                        ┌────────────▼────────────┐
                        │     Claude Tool Use      │
                        │  Structured AI Analysis  │
                        └────────────┬────────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     │               │               │
                  DuckDB          Export          Alerts
               (time-series)   MD / PDF / JSON   Engine
```

---

## Project Structure

```
market-pulse/
├── src/market_pulse/
│   ├── cli/            # Typer commands (watch, report, scan, compare, alert)
│   ├── data/
│   │   ├── sources/    # yahoo.py, alphaV.py, newsapi.py, sec.py, reddit.py
│   │   ├── aggregator.py   # TaskGroup concurrent fan-out
│   │   └── normalizer.py   # → MarketSnapshot
│   ├── analysis/       # technical, fundamental, sentiment, anomaly, comparison
│   ├── ai/             # analyst.py, summarizer.py, scanner.py, prompts.py
│   ├── alerts/         # engine.py, conditions.py, notifiers/
│   ├── storage/        # DuckDB, migrations, diskcache
│   ├── export/         # markdown, json, pdf
│   └── models/         # Pydantic v2 models
└── tests/              # 11 tests — pytest-asyncio, respx HTTP mocking
```

---

## Development

```bash
# Run tests
uv run pytest

# Type check
uv run mypy src/

# Lint
uv run ruff check src/

# Format
uv run ruff format src/
```

---

## License

MIT