import os
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime, time, timedelta
import pytz
import logging
import dash_bootstrap_components as dbc

# Configuration de la journalisation
logging.basicConfig(
    filename='dashboard.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Tableau de Bord de Web Scrapping - Finviz (ANET)"

# Chemins des fichiers (relatifs pour plus de portabilité)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORICAL_FILE = os.path.join(BASE_DIR, 'historical_prices.csv')
RECENT_FILE = os.path.join(BASE_DIR, 'recent_prices.csv')

# Cache pour les données (optimisation des performances)
cached_data = None
last_cache_time = None
CACHE_DURATION = 300  # 5 minutes en secondes

def load_data():
    global cached_data, last_cache_time
    now = datetime.now()

    # Utiliser le cache si les données sont récentes
    if cached_data is not None and last_cache_time is not None:
        if (now - last_cache_time).total_seconds() < CACHE_DURATION:
            logging.info("Utilisation des données en cache")
            return cached_data

    try:
        # Charger les données historiques
        historical = pd.read_csv(HISTORICAL_FILE)
        historical['Date'] = pd.to_datetime(historical['Date'])
        historical = historical.rename(columns={'Date': 'Time', 'Price': 'Price'})
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError) as e:
        logging.error(f"Erreur lors du chargement de historical_prices.csv : {e}")
        historical = pd.DataFrame(columns=['Time', 'Price'])

    try:
        # Charger les données récentes
        recent = pd.read_csv(RECENT_FILE, names=['Time', 'Price'])
        recent['Time'] = pd.to_datetime(recent['Time'])
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError) as e:
        logging.error(f"Erreur lors du chargement de recent_prices.csv : {e}")
        recent = pd.DataFrame(columns=['Time', 'Price'])

    # Combiner les données
    combined = pd.concat([historical, recent], ignore_index=True).sort_values('Time')
    if not combined.empty:
        combined['Time'] = combined['Time'].dt.tz_convert('Europe/Paris')
        # Nettoyer les données (supprimer les valeurs aberrantes)
        combined = combined[combined['Price'].notna() & (combined['Price'] > 0)]
    
    # Mettre à jour le cache
    cached_data = combined
    last_cache_time = now
    logging.info("Données chargées et mises en cache")
    return combined

# Calculer le rapport quotidien pour une date donnée
def daily_report(df, selected_date=None):
    if df.empty:
        return "Aucune donnée disponible pour le rapport quotidien."

    # Utiliser la date sélectionnée ou aujourd'hui par défaut
    if selected_date is None:
        selected_date = datetime.now(pytz.UTC).astimezone(pytz.timezone('Europe/Paris')).date()
    else:
        selected_date = pd.to_datetime(selected_date).date()

    # Filtrer les données pour la date sélectionnée
    df_date = df[df['Time'].dt.date == selected_date]
    
    if df_date.empty:
        return f"Aucune donnée pour le {selected_date.strftime('%Y-%m-%d')}."

    open_price = df_date.iloc[0]['Price']
    close_price = df_date.iloc[-1]['Price']
    volatility = (df_date['Price'].max() - df_date['Price'].min()) / df_date['Price'].mean() * 100
    evolution = (close_price - open_price) / open_price * 100
    avg_price = df_date['Price'].mean()
    
    return (
        f"Rapport Quotidien ({selected_date.strftime('%Y-%m-%d')}) : "
        f"Prix d'ouverture : ${open_price:.2f}, Prix de clôture : ${close_price:.2f}, "
        f"Prix moyen : ${avg_price:.2f}, Volatilité : {volatility:.2f}%, Évolution : {evolution:.2f}%"
    )

# Obtenir le dernier prix
def get_latest_price(df):
    if df.empty:
        return "Prix en temps réel indisponible."
    latest_price = df.iloc[-1]['Price']
    latest_time = df.iloc[-1]['Time'].strftime('%Y-%m-%d %H:%M:%S')
    return f"Prix en temps réel de ANET : ${latest_price:.2f} (à {latest_time})"

# Mise en page améliorée avec Bootstrap
app.layout = dbc.Container([
    html.H1("Tableau de Bord de Web Scrapping - Finviz (ANET)", className="text-center text-light mb-4"),
    
    # Section Rapport Quotidien
    dbc.Row([
        dbc.Col([
            html.H2("Rapport Quotidien", className="text-light"),
            html.Label("Sélectionner une date pour le rapport :", className="text-light"),
            dcc.DatePickerSingle(
                id='report-date-picker',
                date=datetime.now().date(),
                display_format='YYYY-MM-DD',
                className="mb-3"
            ),
            html.H3(id='daily-report', className="text-light"),
        ], width=12)
    ], className="mb-4"),
    
    # Section Prix en Temps Réel
    dbc.Row([
        dbc.Col([
            html.H2("Prix en Temps Réel", className="text-light"),
            html.H3(id='realtime-price', className="text-light"),
        ], width=12)
    ], className="mb-4"),
    
    # Section Graphique et Filtrage
    dbc.Row([
        dbc.Col([
            html.H2("Graphique des Prix", className="text-light"),
            html.Label("Filtrer par Plage de Temps :", className="text-light"),
            dcc.Dropdown(
                id='time-range-dropdown',
                options=[
                    {'label': 'Dernières 10 minutes', 'value': 10},
                    {'label': 'Dernière heure', 'value': 60},
                    {'label': 'Dernier jour', 'value': 1440},  # 24 heures
                    {'label': 'Depuis le Début de l\'Année', 'value': 'year'},
                    {'label': 'Tout', 'value': 'all'}
                ],
                value='year',
                className="mb-3",
                style={'color': '#000000'}  # Texte noir pour lisibilité
            ),
            dcc.Graph(id='price-graph')
        ], width=12)
    ]),
    
    # Intervalle de mise à jour
    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0)  # Mise à jour toutes les 5 minutes
], fluid=True, style={'backgroundColor': '#1E1E1E', 'padding': '20px', 'minHeight': '100vh'})

@app.callback(
    [Output('price-graph', 'figure'),
     Output('daily-report', 'children'),
     Output('realtime-price', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('time-range-dropdown', 'value'),
     Input('report-date-picker', 'date')]
)
def update_dashboard(n, time_range, report_date):
    df = load_data()
    
    # Filtrer les données selon la plage de temps sélectionnée
    now = datetime.now(pytz.UTC).astimezone(pytz.timezone('Europe/Paris'))
    if time_range not in ['all', 'year']:
        cutoff = now - pd.Timedelta(minutes=time_range)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == 'year':
        cutoff = pd.to_datetime('2025-01-01').tz_localize('Europe/Paris')
        df_filtered = df[df['Time'] >= cutoff]
    else:
        df_filtered = df
    
    # Créer le graphique avec des annotations
    fig = px.line(df_filtered, x='Time', y='Price', title='Prix de ANET au fil du Temps (Scrappé Toutes les 5 Minutes)')
    fig.update_layout(
        plot_bgcolor='#333333',
        paper_bgcolor='#333333',
        font_color='#FFFFFF',
        title_font_color='#FFFFFF',
        xaxis_gridcolor='#444444',
        yaxis_gridcolor='#444444',
        hovermode='x unified'
    )
    fig.update_traces(line_color='#00CC96', line_width=2)
    
    # Ajouter une annotation pour le dernier prix
    if not df_filtered.empty:
        latest = df_filtered.iloc[-1]
        fig.add_annotation(
            x=latest['Time'],
            y=latest['Price'],
            text=f"${latest['Price']:.2f}",
            showarrow=True,
            arrowhead=2,
            ax=20,
            ay=-30,
            font=dict(color='#FFFFFF')
        )
    
    # Mettre à jour le rapport quotidien pour la date sélectionnée
    report = daily_report(df, report_date)
    
    # Mettre à jour le prix en temps réel
    realtime = get_latest_price(df)
    
    return fig, report, realtime

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)  # Désactiver debug en production
