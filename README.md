# South Glos Bin Collection Calendar

Generates a subscribable iCal feed for South Gloucestershire bin collections, updated nightly via GitHub Actions.

## Setup

### 1. Fork / create this repo on GitHub

Make sure it's **public** (required for free GitHub Pages hosting).

### 2. Add your UPRN as a secret

Go to **Settings → Secrets and variables → Actions → New repository secret**:

- Name: `UPRN`
- Value: your UPRN (e.g. `100012345678`)

### 3. Enable GitHub Pages

Go to **Settings → Pages**:

- Source: **Deploy from a branch**
- Branch: `main`, folder: `/docs`
- Save

Your calendar will be available at:
```
https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/calendar.ics
```

### 4. Run the workflow manually first

Go to **Actions → Update Bin Calendar → Run workflow** to generate the initial `calendar.ics`.

### 5. Subscribe in your calendar app

**Google Calendar:** Settings → Add calendar → From URL → paste the URL above

**Apple Calendar:** File → New Calendar Subscription → paste the URL above

## How it works

- Calls `https://api.southglos.gov.uk/wastecomp/GetCollectionDetails?uprn=YOUR_UPRN`
- Reads the next collection date and schedule (weekly/fortnightly) for each service
- Projects dates 26 weeks forward
- Writes a `.ics` file with a reminder alarm the evening before each collection
- GitHub Actions runs this every night at 8pm UTC and commits any changes

## Running locally

```bash
pip install -r requirements.txt
UPRN=100012345678 python generate_calendar.py
```

## File structure 
```
auto-bin-collection/
├── .github/
│   └── workflows/
│       └── update.yml
├── docs/
│   └── calendar.ics        ← generated, not in repo yet (created on first run)
├── generate_calendar.py
├── README.md
└── requirements.txt
```
