# 🕸️ Web Scraping Project – ANET (Finviz)

This project scrapes the stock price of **Arista Networks (ANET)** from **Finviz** and displays the data in an interactive **Dash dashboard**.

---

## 📌 Features

- ⏱️ **Automated scraping every 5 minutes** via a Bash script (`scrape.sh`).
- 💾 **Data storage**:
  - `historical_prices.csv`: enriched manually for long-term visualizations.
  - `recent_prices.csv`: updated every 5 minutes via `crontab`.
- 📊 **Interactive dashboard** (`app.py`) includes:
  - Time-series chart with a **customizable SMA (Simple Moving Average)**.
  - **Daily report**: opening price, closing price, average, volatility, and performance.
  - **Period report**: for a custom date range (open, close, volatility, performance).
  - **Global statistics**: min, max, average, volatility.
  - **Real-time price** with percentage change.
  - Option to **export filtered data** to CSV.
  - **Auto-refresh every 5 minutes** using Dash’s `dcc.Interval`.

---

## ⚙️ Requirements

- Python 3.12  
- Git  
- `curl` (for scraping)  
- Cron (for automation)  
- EC2 instance (optional for web hosting)

---

## 🛠️ Installation

# 1. Clone the repository
git clone https://github.com/your-username/web-scrapping.git
cd web-scrapping

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the dashboard in background
nohup python3 app.py &

You can then access the dashboard at:
http://<your-ip>:8050
Replace <your-ip> with your local or EC2 IP address.

---

## ⏲️ Set Up Cron Job (Optional)

To automate scraping every 5 minutes:

# 1. Make the script executable
chmod +x scrape.sh

# 2. Open crontab
crontab -e

# 3. Add this line (replace path accordingly)
*/5 * * * * /path/to/web-scrapping/scrape.sh >> /path/to/web-scrapping/cron.log 2>&1

---

## 📁 Key Files and Structure

web-scrapping/
├── app.py                  # Dash dashboard
├── scrape.sh               # Scraping script (Finviz)
├── prices.txt              # Raw scraped output
├── recent_prices.csv       # Latest data (every 5 min)
├── historical_prices.csv   # Enriched historical data
├── historicaldata.py       # Data utilities (optional)
├── dashboard.log           # Dashboard logs
├── debug.log               # scrape.sh logs
├── cron.log                # Cron job output
├── nohup.out               # Output from background execution
├── requirements.txt        # Python dependencies
├── .gitignore              # Files excluded from Git
├── source/                 # Additional scripts (if any)
└── venv/                   # Python virtual environment

## 👥 Authors

    Vithusan KAILASAPILLAI

    Rudy LOGGHE



