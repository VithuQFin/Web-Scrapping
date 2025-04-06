from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime, time
import pytz

app = Dash(__name__)
app.title = "Tableau de Bord de Web Scrapping - Finviz (ANET)"

# Charger les données (historiques et récentes)
def load_data():
    # Charger les données historiques
    try:
        historical = pd.read_csv('/home/ubuntu/Web-Scrapping/historical_prices.csv')
        historical['Date'] = pd.to_datetime(historical['Date'])
        historical = historical.rename(columns={'Date': 'Time', 'Price': 'Price'})
    except FileNotFoundError:
        historical = pd.DataFrame(columns=['Time', 'Price'])

    # Charger les données récentes
    try:
        recent = pd.read_csv('/home/ubuntu/Web-Scrapping/recent_prices.csv', names=['Time', 'Price'])
        recent['Time'] = pd.to_datetime(recent['Time'])
    except FileNotFoundError:
        recent = pd.DataFrame(columns=['Time', 'Price'])

    # Combiner les données
    combined = pd.concat([historical, recent], ignore_index=True).sort_values('Time')
    # Convertir les horodatages en Europe/Paris
    combined['Time'] = combined['Time'].dt.tz_convert('Europe/Paris')
    return combined

# Calculer le rapport quotidien (mis à jour à 20h)
def daily_report(df):
    if df.empty:
        return "Aucune donnée disponible pour le rapport quotidien."
    
    # Filtrer les données pour aujourd'hui
    today = datetime.now(pytz.UTC).astimezone(pytz.timezone('Europe/Paris')).date()
    df_today = df[df['Time'].dt.date == today]
    
    if df_today.empty:
        return "Aucune donnée pour aujourd'hui."
    
    open_price = df_today.iloc[0]['Price']
    close_price = df_today.iloc[-1]['Price']
    volatility = (df_today['Price'].max() - df_today['Price'].min()) / df_today['Price'].mean() * 100
    evolution = (close_price - open_price) / open_price * 100
    
    return f"RAPPORT QUOTIDIEN (Mis à jour à 20H) : Prix d'ouverture : ${open_price:.2f}, Prix de clôture : ${close_price:.2f}, Volatilité : {volatility:.2f}%, Évolution : {evolution:.2f}%"

# Obtenir le dernier prix pour affichage
def get_latest_price(df):
    if df.empty:
        return "Prix en temps réel indisponible."
    latest_price = df.iloc[-1]['Price']
    return f"Prix en temps réel de ANET : ${latest_price:.2f}"

app.layout = html.Div([
    html.H1("Tableau de Bord de Web Scrapping - Finviz (ANET)", style={'textAlign': 'center', 'color': '#FFFFFF'}),
    html.Div([
        html.H2("Rapport Quotidien", style={'color': '#FFFFFF'}),
        html.H3(id='daily-report', style={'color': '#FFFFFF'}),
        html.H2("Prix en Temps Réel", style={'color': '#FFFFFF'}),
        html.H3(id='realtime-price', style={'color': '#FFFFFF'}),
        html.H2("Filtrer par Plage de Temps", style={'color': '#FFFFFF'}),
        dcc.Dropdown(
            id='time-range-dropdown',
            options=[
                {'label': 'Dernières 10 minutes', 'value': 10},
                {'label': 'Dernière heure', 'value': 60},
                {'label': 'Depuis le Début de l\'Année', 'value': 'year'},
                {'label': 'Tout', 'value': 'all'}
            ],
            value='year',
            style={'width': '50%', 'margin': '10px auto', 'backgroundColor': '#333333', 'color': '#FFFFFF'}
        ),
        dcc.Graph(id='price-graph')
    ], style={'margin': '20px'}),
    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0)  # Mise à jour toutes les 5 minutes
], style={'backgroundColor': '#1E1E1E', 'padding': '20px', 'minHeight': '100vh'})

@app.callback(
    [Output('price-graph', 'figure'),
     Output('daily-report', 'children'),
     Output('realtime-price', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('time-range-dropdown', 'value')]
)
def update_dashboard(n, time_range):
    df = load_data()
    
    # Filtrer les données selon la plage de temps sélectionnée
    if time_range not in ['all', 'year']:
        cutoff = datetime.now(pytz.UTC).astimezone(pytz.timezone('Europe/Paris')) - pd.Timedelta(minutes=time_range)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == 'year':
        cutoff = pd.to_datetime('2025-01-01').tz_localize('Europe/Paris')
        df_filtered = df[df['Time'] >= cutoff]
    else:
        df_filtered = df
    
    # Créer le graphique
    fig = px.line(df_filtered, x='Time', y='Price', title='Prix de ANET au fil du Temps (Données Scrappées Toutes les 5 Minutes)')
    fig.update_layout(
        plot_bgcolor='#333333',
        paper_bgcolor='#333333',
        font_color='#FFFFFF',
        title_font_color='#FFFFFF',
        xaxis_gridcolor='#444444',
        yaxis_gridcolor='#444444'
    )
    
    # Mettre à jour le rapport quotidien (seulement à 20h)
    now = datetime.now(pytz.UTC).astimezone(pytz.timezone('Europe/Paris'))
    report = daily_report(df) if now.time() >= time(20, 0) else None
    
    # Mettre à jour le prix en temps réel
    realtime = get_latest_price(df)
    
    return fig, report, realtime

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)
