# 🗑️ SGC Bin Collection Calendar

Automatically fetches bin collection dates from South Gloucestershire Council and publishes them as a live `.ics` calendar feed via GitHub Pages.

The calendar updates every night at 11pm UTC via GitHub Actions. No address or identifying information is stored in the code — everything sensitive is kept in GitHub Actions Secrets.

---

## Setup (one time only)

### 1. Create the repo

- Create a new **public** repository on GitHub (e.g. `bin-calendar`)
- Upload all the files from this folder, preserving the folder structure

### 2. Find your UPRN

You need to do this once locally so you never have to put your address in the repo.

Make sure you have Python and the `requests` library installed:

```bash
pip install requests
```

Run the script with your house number and postcode to find your UPRN:

```bash
export SGC_HOUSE=YOUR_HOUSE_NUMBER
export SGC_POSTCODE="YOUR_POSTCODE"
python sgc_bin_calendar.py
```

It will print something like `Address matched. UPRN: 123456789012` — copy that number.

> **Windows users:** use `set` instead of `export`:
> ```
> set SGC_HOUSE=YOUR_HOUSE_NUMBER
> set SGC_POSTCODE=YOUR_POSTCODE
> python sgc_bin_calendar.py
> ```

### 3. Add your UPRN as a GitHub Secret

- Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions**
- Click **New repository secret**
- Name: `SGC_UPRN`
- Value: your UPRN (e.g. `123456789012`)
- Click **Add secret**

Your UPRN is now encrypted and only visible to GitHub Actions — not to anyone browsing your repo.

### 4. Enable GitHub Pages

- Go to your repo → **Settings** → **Pages**
- Under *Source*, select **Deploy from a branch**
- Set branch to `main` (or `master`) and folder to `/docs`
- Click **Save**

After a minute or two, your Pages site will be live at:
`https://YOUR-USERNAME.github.io/bin-calendar/`

### 5. Run the workflow for the first time

- Go to your repo → **Actions** tab
- Click **Update Bin Calendar** in the left sidebar
- Click **Run workflow** → **Run workflow**

This generates `docs/bin_collections.ics` and commits it to the repo. After that it runs automatically every night.

### 6. Subscribe your calendar app

Your subscription URL is:

```
https://YOUR-USERNAME.github.io/bin-calendar/bin_collections.ics
```

- **Google Calendar:** Settings → Add other calendars → From URL → paste URL
- **Apple Calendar:** File → New Calendar Subscription → paste URL
- **Outlook:** Add calendar → Subscribe from web → paste URL

---

## What's private, what's public

| Thing | Visible publicly? |
|---|---|
| Your UPRN | ❌ No — stored as an encrypted GitHub Secret |
| Your house number / postcode | ❌ No — never stored anywhere in the repo |
| The `.ics` file (bin dates only) | ✅ Yes — intentionally, so your calendar app can read it |
| The workflow and Python code | ✅ Yes — but contains no identifying information |

---

## Troubleshooting

**The workflow fails with "No UPRN or address supplied"**
Check that the `SGC_UPRN` secret is set correctly under Settings → Secrets and variables → Actions.

**"No addresses found" when running locally**
Double-check your postcode includes a space (e.g. `BS12 3AB`).

**"No collection dates returned"**
The SGC API URL may have changed. Check [beta.southglos.gov.uk](https://beta.southglos.gov.uk/waste-and-recycling-collection-date/) and update the URL in `get_collections()` in the script.

---

## Files

| File | Purpose |
|---|---|
| `sgc_bin_calendar.py` | Fetches dates from SGC API and writes the `.ics` file |
| `.github/workflows/update-calendar.yml` | Schedules the script to run nightly via GitHub Actions |
| `docs/index.html` | Simple page showing your subscription URL |
| `docs/bin_collections.ics` | Generated automatically — do not edit manually |
