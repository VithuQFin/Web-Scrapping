import yfinance as yf
import pandas as pd

def historical_data(ticker="ANET", start_date="2025-01-01", end_date="2025-04-05"):
    try:
        # Télécharger les données historiques avec yfinance
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            print(f"Aucune donnée trouvée pour {ticker} entre {start_date} et {end_date}")
            return
        
        # Extraire la colonne 'Close' (prix de clôture) et la date
        data = data[['Close']].reset_index()
        data.columns = ['Date', 'Price']
        
        # Convertir la date au format ISO 8601
        data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        
        # Enregistrer dans historical_prices.csv
        data.to_csv('/home/ubuntu/Web-Scrapping/historical_prices.csv', index=False)
        print(f"Données historiques pour {ticker} enregistrées dans historical_prices.csv")
    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")

if __name__ == "__main__":
    historical_data()
