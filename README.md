# AI Development Analyst

Collects data about the AI tools landscape (GitHub, Reddit, YouTube, newsletters),
stores it in SQLite with categories and quality scores, and shows it in a Streamlit dashboard.
This is an educational project, built step by step.

## Setup (once)
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then add your keys (optional for now)
```

## Run
```bash
python collect.py --sample   # offline sample data, no keys or network needed
python collect.py            # real GitHub data (run this on your own machine)
pytest                       # run the tests
```
Sample items are tagged `[SAMPLE]` and come from `fixtures/`.

## Progress
- [x] Step 1: project setup, SQLite schema (`db.py`), GitHub collector
- [ ] Step 2: newsletter (RSS) collector
- [ ] Step 3: Reddit + YouTube collectors
- [ ] Step 4: categories, quality scores
- [ ] Step 5: Streamlit dashboard with filters and search
