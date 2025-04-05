import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime, time
import os
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pytz

app = dash.Dash(__name__)

# Fonction pour scraper le prix en temps réel
def scrape_price_realtime():
    try:
        url = 'https://finviz.com/quote.ashx?t=ANET'
        req = Request(url=url, headers={'user-agent': 'my-app'})
        response = urlopen(req)
        html = BeautifulSoup(response, 'html.parser')
        price_element = html.find('strong', class_='quote-price_wrapper_price')
        if price_element:
            price = price_element.text.strip()
            return float(price.replace(',', ''))
        return None
    except Exception as e:
        return None

# Lire les données scrapées par le script bash
def load_data():
    if not os.path.exists('prices.txt'):
        return pd.DataFrame({'Time': [], 'Price': []})
    df = pd.read_csv('prices.txt', names=['Time', 'Price'])
    df['Time'] = pd.to_datetime(df['Time']).dt.tz_localize('UTC').dt.tz_convert('Europe/Paris')
    df['Price'] = df['Price'].astype(float)
    return df

# Calculer le rapport quotidien (mis à jour à 20h)
def daily_report():
    df = load_data()
    if df.empty:
        return "Aucune donnée disponible pour le rapport quotidien."
    today = datetime.now().date()
    df_today = df[df['Time'].dt.date == today]
    if df_today.empty:
        return "Aucune donnée pour aujourd'hui."
    open_price = df_today['Price'].iloc[0]
    close_price = df_today['Price'].iloc[-1]
    volatility = (df_today['Price'].max() - df_today['Price'].min()) / df_today['Price'].mean() * 100
    evolution = ((close_price - open_price) / open_price) * 100
    return f"Rapport Quotidien (mis à jour à 20h) : Prix d'ouverture : ${open_price:,.2f}, Prix de clôture : ${close_price:,.2f}, Volatilité : {volatility:.2f}%, Évolution : {evolution:.2f}%"

# Obtenir le prix en temps réel pour affichage
def get_realtime_price():
    price = scrape_price_realtime()
    if price:
        return f"Prix en temps réel de ANET : ${price:,.2f}"
    return "Prix en temps réel indisponible."

# Mise en page initiale du tableau de bord
app.layout = html.Div([
    html.H1("Tableau de Bord de Scraping - Finviz (ANET)"),
    dcc.Graph(id='price-graph'),
    html.H2("Rapport Quotidien"),
    html.Div(id='daily-report'),
    html.H2("Prix en Temps Réel"),
    html.Div(id='realtime-price'),
    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0)  # Mise à jour toutes les 5 minutes
])

@app.callback(
    [Output('price-graph', 'figure'),
     Output('daily-report', 'children'),
     Output('realtime-price', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    # Recharger les données
    df = load_data()
    fig = px.line(df, x='Time', y='Price', title='Prix de ANET au Fil du Temps (Données Scrapées Toutes les 5 Minutes)')
    
    # Mettre à jour le rapport quotidien (seulement à 20h)
    now = datetime.now()
    report = daily_report() if now.time() >= time(20, 0) else dash.no_update
    
    # Mettre à jour le prix en temps réel
    realtime = get_realtime_price()
    
    return fig, report, realtime

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime, time
import os
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pytz

app = dash.Dash(__name__)

# Fonction pour scraper le prix en temps réel
def scrape_price_realtime():
    try:
        url = 'https://finviz.com/quote.ashx?t=ANET'
        req = Request(url=url, headers={'user-agent': 'my-app'})
        response = urlopen(req)
        html = BeautifulSoup(response, 'html.parser')
        price_element = html.find('strong', class_='quote-price_wrapper_price')
        if price_element:
            price = price_element.text.strip()
            return float(price.replace(',', ''))
        return None
    except Exception as e:
        return None

# Lire les données scrapées par le script bash
def load_data():
    if not os.path.exists('prices.txt'):
        return pd.DataFrame({'Time': [], 'Price': []})
    df = pd.read_csv('prices.txt', names=['Time', 'Price'])
    df['Time'] = pd.to_datetime(df['Time']).dt.tz_localize('UTC').dt.tz_convert('Europe/Paris')
    df['Price'] = df['Price'].astype(float)
    return df

# Calculer le rapport quotidien (mis à jour à 20h)
def daily_report():
    df = load_data()
    if df.empty:
        return "Aucune donnée disponible pour le rapport quotidien."
    today = datetime.now().date()
    df_today = df[df['Time'].dt.date == today]
    if df_today.empty:
        return "Aucune donnée pour aujourd'hui."
    open_price = df_today['Price'].iloc[0]
    close_price = df_today['Price'].iloc[-1]
    volatility = (df_today['Price'].max() - df_today['Price'].min()) / df_today['Price'].mean() * 100
    evolution = ((close_price - open_price) / open_price) * 100
    return f"Rapport Quotidien (mis à jour à 20h) : Prix d'ouverture : ${open_price:,.2f}, Prix de clôture : ${close_price:,.2f}, Volatilité : {volatility:.2f}%, Évolution : {evolution:.2f}%"

# Obtenir le prix en temps réel pour affichage
def get_realtime_price():
    price = scrape_price_realtime()
    if price:
        return f"Prix en temps réel de ANET : ${price:,.2f}"
    return "Prix en temps réel indisponible."

app.layout = html.Div([
    html.H1("Tableau de Bord de Scraping - Finviz (ANET)", style={'textAlign': 'center', 'color': '#FFFFFF'}),
    dcc.Graph(id='price-graph'),
    html.H2("Rapport Quotidien", style={'textAlign': 'center', 'color': '#FFFFFF'}),
    html.Div(id='daily-report', style={'textAlign': 'center', 'color': '#FFFFFF'}),
    html.H2("Prix en Temps Réel", style={'textAlign': 'center', 'color': '#FFFFFF'}),
    html.Div(id='realtime-price', style={'textAlign': 'center', 'color': '#FFFFFF'}),
    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0)
], style={
    'background': '#1C2526',  # Solid dark navy blue for testing
    'minHeight': '100vh',
    'padding': '20px'
})
