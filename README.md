# WebMD Drug Names Scraper

This project scrapes drug names from WebMD (letters `a`–`z` and `0`) and saves the results to `drugs_list.csv` and `drugs_list.json`.

The scraper uses Selenium (Firefox / geckodriver) + BeautifulSoup and `webdriver-manager` to auto-manage drivers. This README shows how to install and run the project using **uv (Astral)** as the dependency & environment manager.

---

## Requirements

- Firefox browser installed.
- Internet connection (the scraper visits WebMD pages).
- `curl` or PowerShell for the `uv` installer (optional).

---

## Quick overview

1. Install `uv` (Astral) — the dependency manager.
2. Initialize or use a project with `uv`.
3. Install dependencies: `selenium`, `beautifulsoup4`, `lxml`, `webdriver-manager`.
4. Run the scraper script (`main.py`) using `uv run` or by activating the environment.
5. Outputs are written to `drugs_list.csv` and `drugs_list.json` in the project root.

---

## Install `uv` (Astral)

macOS / Linux (recommended):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify:

```bash
uv --version
```

---

## Install dependency & Activate environtment

Open a terminal in the project folder and follow these commands.

1. Install dependencies:

```bash
uv sync
```

2. Activate venv:

```bash
# macOS / Linux
source .venv/bin/activate
python main.py

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
python main.py
```

---

## Run the scraper

```bash
uv run python main.py
```

---

## Outputs

After the run completes, the script saves:

- `drugs_list.csv` — CSV with columns: `Alphabet, Drug Name, Link`.
- `drugs_list.ndjson` — JSON grouped by alphabet.

Files are written to the project root (same folder as `main.py`) unless changed in the script.
