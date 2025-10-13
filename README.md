# Hockey Fantasy Salary Cap Tool 
Get NHL player salaries for your Fantrax fantasy league without paying for the premium salary cap feature!

## Overview
This tool scrapes NHL salary data from the web and calculates salary cap totals for your Fantrax fantasy hockey league. Instead of paying for Fantrax's premium features, use this free solution to track your league's salary cap.
## Setup
### 1. (Optional) Create a Conda Environment

```bash
conda create -n Hockey_Fantasy python=3.12 -y
conda activate Hockey_Fantasy
```

### 2. Clone and Install
```bash
git clone https://github.com/Fred-Lanthier/Hockey_Fantasy.git
cd Hockey_Fantasy
pip3 install -r requirements.txt
```

## How to Use
### Step 1: Build Your Salary Database (One-Time Setup)
This step scrapes the web for all NHL player salaries. Only do this once per season as it takes time.

Download all players from Fantrax:

- Go to your league → Players tab
- In Status/Team dropdown, select "All"
- Click the download CSV button: <img width="64" height="62" alt="image" src="https://github.com/user-attachments/assets/0cc2c74d-e415-4982-af51-56ff5343fb55" />
- Place the file in `Datas/` folder

Run the scraper:
```bash
 python3 Salary_Scrap.py --input Datas/<YOUR_FILE>.csv --action get
```

This creates `Output_Datas/Player_Salaries.csv` - your salary database for the season.

### Step 2: Calculate Team Salary Totals (Use Anytime)
This step is fast and can be run as often as you want.

Download your league's current rosters:

- Go to your league → Players tab
- In Status/Team dropdown, select "All taken players"
- Click the download CSV button
- Place the file in `Datas/` folder
- Optional: Rename it with the date or week number (e.g., `Week_10.csv`) to track changes over time

Calculate totals:
```bash
 python3 Salary_Scrap.py --input Datas/<YOUR_FILE>.csv --action totals
```

## View results:

Open `Output_Datas/<YOUR_FILE>-totals.csv`

See each player, their owner (Status), and salary

Team totals appear after each manager's roster
Quick Reference
| Command | Purpose | When to Use |
| :--- | :--- | :--- |
| --action get | Scrape all NHL salaries | Once per season (slow) |
| --action totals | Calculate team cap totals | Anytime (fast) |

## File Structure
```
Hockey_Fantasy/
├── Datas/                          # Put your downloaded CSVs here
├── Output_Datas/
│   ├── Player_Salaries.csv        # Salary database (created by --action get)
│   └── *-totals.csv               # Team totals (created by --action totals)
├── Salary_Scrap.py                # Main script
└── requirements.txt
```
## Example Workflow
```bash
# One-time setup (beginning of season)
python3 Salary_Scrap.py --input Datas/All_Players_2025.csv --action get

# Weekly salary cap checks (instant)
python3 Salary_Scrap.py --input Datas/Week_1.csv --action totals
python3 Salary_Scrap.py --input Datas/Week_2.csv --action totals
python3 Salary_Scrap.py --input Datas/Week_3.csv --action totals
```

Enjoy free salary cap tracking!







