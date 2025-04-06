from dash import dcc, html, Dash, callback_context
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime, time
import pytz

app = Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'])
app.title = "Tableau de Bord de Web Scrapping - Finviz (ANET)"

# Charger les données (historiques et récentes)
def load_data():
    try:
        historical = pd.read_csv('/home/ec2-user/Web-Scrapping/historical_prices.csv')
        historical['Date'] = pd.to_datetime(historical['Date'])
        historical = historical.rename(columns={'Date': 'Time', 'Price': 'Price'})
    except FileNotFoundError:
        historical = pd.DataFrame(columns=['Time', 'Price'])

    try:
        recent = pd.read_csv('/home/ec2-user/Web-Scrapping/recent_prices.csv', names=['Time', 'Price'])
        recent['Time'] = pd.to_datetime(recent['Time'])
    except FileNotFoundError:
        recent = pd.DataFrame(columns=['Time', 'Price'])

    combined = pd.concat([historical, recent], ignore_index=True).sort_values('Time')
    combined['Time'] = combined['Time'].dt.tz_convert('Europe/Paris')
    return combined

# Calculer le rapport quotidien (mis à jour à 20h)
def daily_report(df):
    if df.empty:
        return "Aucune donnée disponible pour le rapport quotidien."
    
    today = datetime.now(pytz.UTC).astimezone(pytz.timezone('Europe/Paris')).date()
    df_today = df[df['Time'].dt.date == today]
    
    if df_today.empty:
        return "Aucune donnée pour aujourd'hui."
    
    open_price = df_today.iloc[0]['Price']
    close_price = df_today.iloc[-1]['Price']
    volatility = (df_today['Price'].max() - df_today['Price'].min()) / df_today['Price'].mean() * 100
    evolution = (close_price - open_price) / open_price * 100
    
    return f"Prix d'ouverture : ${open_price:.2f}, Prix de clôture : ${close_price:.2f}, Volatilité : {volatility:.2f}%, Évolution : {evolution:.2f}%"

# Calculer le rapport pour la période sélectionnée
def period_report(df_filtered):
    if df_filtered.empty:
        return "Aucune donnée pour la période sélectionnée."
    
    open_price = df_filtered.iloc[0]['Price']
    close_price = df_filtered.iloc[-1]['Price']
    volatility = (df_filtered['Price'].max() - df_filtered['Price'].min()) / df_filtered['Price'].mean() * 100
    evolution = (close_price - open_price) / open_price * 100
    
    return f"Prix d'ouverture : ${open_price:.2f}, Prix de clôture : ${close_price:.2f}, Volatilité : {volatility:.2f}%, Évolution : {evolution:.2f}%"

# Obtenir le dernier prix et le changement en pourcentage
def get_latest_price_and_change(df):
    if df.empty:
        return "Prix en temps réel indisponible.", 0.0
    latest_price = df.iloc[-1]['Price']
    previous_price = df.iloc[-2]['Price'] if len(df) > 1 else latest_price
    price_change = (latest_price - previous_price) / previous_price * 100 if previous_price != 0 else 0
    return f"${latest_price:.2f}", price_change

# Obtenir les statistiques clés
def get_key_metrics(df):
    if df.empty:
        return {"high": 0, "low": 0, "avg": 0}
    high = df['Price'].max()
    low = df['Price'].min()
    avg = df['Price'].mean()
    return {"high": high, "low": low, "avg": avg}

# Calculer les SMA pour la période sélectionnée
def calculate_sma_for_period(df_filtered):
    if df_filtered.empty:
        return {"sma10": 0, "sma20": 0, "sma50": 0}
    
    sma10 = df_filtered['Price'].rolling(window=10, min_periods=1).mean().iloc[-1]
    sma20 = df_filtered['Price'].rolling(window=20, min_periods=1).mean().iloc[-1]
    sma50 = df_filtered['Price'].rolling(window=50, min_periods=1).mean().iloc[-1]
    
    return {
        "sma10": sma10 if not pd.isna(sma10) else 0,
        "sma20": sma20 if not pd.isna(sma20) else 0,
        "sma50": sma50 if not pd.isna(sma50) else 0
    }

# Define the block content for fixed layout
block_content = [
    # Real-Time Price Card
    html.Div([
        html.H2("Prix en Temps Réel", className="text-lg font-semibold text-gray-200 mb-2"),
        html.H3(id='realtime-price', className="text-xl font-bold text-green-400"),
        html.P(id='price-change', className="text-sm mt-2"),
    ], className="bg-gray-700 p-4 rounded-lg shadow-md flex-1 mx-2 min-w-[200px]"),

    # Key Metrics Card
    html.Div([
        html.H2("Statistiques Clés", className="text-lg font-semibold text-gray-200 mb-2"),
        html.P(id='key-metrics-high', className="text-gray-400"),
        html.P(id='key-metrics-low', className="text-gray-400"),
        html.P(id='key-metrics-avg', className="text-gray-400"),
    ], className="bg-gray-700 p-4 rounded-lg shadow-md flex-1 mx-2 min-w-[200px]"),

    # Daily Report Card
    html.Div([
        html.H2("Rapport Quotidien (Mis à jour à 20h)", className="text-lg font-semibold text-gray-200 mb-2"),
        html.P(id='daily-report', className="text-gray-400"),
    ], className="bg-gray-700 p-4 rounded-lg shadow-md flex-1 mx-2 min-w-[200px]"),

    # Period Report Card
    html.Div([
        html.H2("Rapport Période (Période Sélectionnée)", className="text-lg font-semibold text-gray-200 mb-2"),
        html.P(id='period-report', className="text-gray-400"),
    ], className="bg-gray-700 p-4 rounded-lg shadow-md flex-1 mx-2 min-w-[200px]"),

    # SMA Period Card
    html.Div([
        html.H2("Période de la Moyenne Mobile", className="text-lg font-semibold text-gray-200 mb-2"),
        html.P(id='sma-10', className="text-gray-400"),
        html.P(id='sma-20', className="text-gray-400"),
        html.P(id='sma-50', className="text-gray-400"),
    ], className="bg-gray-700 p-4 rounded-lg shadow-md flex-1 mx-2 min-w-[200px]"),
]

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Tableau de Bord de Web Scrapping - Finviz (ANET)", className="text-3xl font-bold text-gray-200 text-center mb-4"),
        html.P("Suivi en temps réel des prix de ANET via Finviz", className="text-lg text-gray-400 text-center mb-6")
    ], className="bg-gray-800 p-6 rounded-lg shadow-lg mb-6"),

    # Main Content
    html.Div([
        # Fixed Blocks Section
        html.Div(
            block_content,
            className="flex flex-wrap gap-4 mb-6"
        ),

        # Graph and Filter Section
        html.Div([
            # Graph Header
            html.Div([
                html.H2("Graphique des Prix", className="text-lg font-semibold text-gray-200 mb-2"),
                html.Small("Filtrer et personnaliser", className="text-gray-400")
            ], className="mb-4"),

            # Time Range Filter
            html.Label("Plage de Temps :", className="text-gray-200 mb-2"),
            dcc.Dropdown(
                id='time-range-dropdown',
                options=[
                    {'label': 'Tout', 'value': 'all'},
                    {'label': '5 Ans', 'value': '5years'},
                    {'label': '1 An', 'value': '1year'},
                    {'label': 'YTD', 'value': 'ytd'},
                    {'label': '1 Jour', 'value': 1440},
                    {'label': '1 heure', 'value': 60},
                    {'label': '10 dernières minutes', 'value': 10},
                ],
                value='1year',
                className="mb-4 p-2 rounded bg-gray-600 text-gray-200"
            ),

            # SMA Period Filter
            html.Label("Période de la Moyenne Mobile :", className="text-gray-200 mb-2"),
            dcc.Dropdown(
                id='sma-period-dropdown',
                options=[
                    {'label': 'SMA 10', 'value': 10},
                    {'label': 'SMA 20', 'value': 20},
                    {'label': 'SMA 50', 'value': 50},
                ],
                value=20,
                className="mb-4 p-2 rounded bg-gray-600 text-gray-200"
            ),

            # Price Graph
            dcc.Graph(id='price-graph', config={'displayModeBar': True}, className="bg-gray-700 p-4 rounded-lg shadow-md"),

            # Download Button
            html.Button(
                "Télécharger les Données (CSV)",
                id='download-button',
                className="inline-block mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            ),
            dcc.Download(id="download-dataframe-csv"),
        ], className="w-full p-4"),
    ], className="flex flex-col gap-6"),
    
    # Update Interval
    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0)
], className="bg-gray-800 min-h-screen p-6")

@app.callback(
    [Output('price-graph', 'figure'),
     Output('realtime-price', 'children'),
     Output('price-change', 'children'),
     Output('key-metrics-high', 'children'),
     Output('key-metrics-low', 'children'),
     Output('key-metrics-avg', 'children'),
     Output('daily-report', 'children'),
     Output('period-report', 'children'),
     Output('sma-10', 'children'),
     Output('sma-20', 'children'),
     Output('sma-50', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('time-range-dropdown', 'value'),
     Input('sma-period-dropdown', 'value')]
)
def update_dashboard(n, time_range, sma_period):
    df = load_data()
    
    # Filtrer les données selon la plage de temps sélectionnée
    now = datetime.now(pytz.UTC).astimezone(pytz.timezone('Europe/Paris'))
    if time_range not in ['all', '5years', '1year', 'ytd']:
        cutoff = now - pd.Timedelta(minutes=time_range)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '5years':
        cutoff = now - pd.Timedelta(days=5*365)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '1year':
        cutoff = now - pd.Timedelta(days=365)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == 'ytd':
        cutoff = pd.to_datetime(f"{now.year}-01-01").tz_localize('Europe/Paris')
        df_filtered = df[df['Time'] >= cutoff]
    else:
        df_filtered = df
    
    # S'assurer que les données sont triées
    df_filtered = df_filtered.sort_values('Time')

    # Calculer la moyenne mobile pour le graphique
    sma_label = f"SMA_{sma_period}"
    df_filtered[sma_label] = df_filtered['Price'].rolling(window=sma_period, min_periods=1).mean()

    # Créer le graphique
    fig = px.line(df_filtered, x='Time', y=['Price', sma_label],
                  labels={'value': 'Prix ($)', 'variable': 'Ligne'},
                  title='Évolution de ANET (Scraping toutes les 5 minutes)')
    fig.update_layout(
        plot_bgcolor='#1C2526',  # Navy blue background
        paper_bgcolor='#1C2526',  # Navy blue paper background
        font_color='#D1D5DB',
        title_font_color='#D1D5DB',
        xaxis_gridcolor='#4B5563',
        yaxis_gridcolor='#4B5563',
        title_font_size=20,
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode='x unified',
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date'
        )
    )
    fig.update_traces(line_width=2, selector=dict(name='Price'), line_color='#1F77B4')  # Fixed blue color for price line
    fig.update_traces(line_width=1, line_dash='dash', selector=dict(name=sma_label))

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
            font=dict(color='#D1D5DB')
        )

    # Mettre à jour le prix en temps réel et le changement
    realtime, change = get_latest_price_and_change(df)
    change_text = f"Changement: {'+' if change >= 0 else ''}{change:.2f}%"
    change_color = "text-green-400" if change >= 0 else "text-red-400"
    change_text = html.Span(change_text, className=change_color)

    # Mettre à jour les statistiques clés
    metrics = get_key_metrics(df_filtered)
    high_text = f"Prix le plus haut: ${metrics['high']:.2f}"
    low_text = f"Prix le plus bas: ${metrics['low']:.2f}"
    avg_text = f"Prix moyen: ${metrics['avg']:.2f}"

    # Mettre à jour le rapport quotidien (seulement à 20h)
    now = datetime.now(pytz.UTC).astimezone(pytz.timezone('Europe/Paris'))
    daily = daily_report(df) if now.time() >= time(20, 0) else "Rapport non disponible avant 20h."

    # Mettre à jour le rapport de la période sélectionnée
    period = period_report(df_filtered)

    # Calculer les SMA pour le bloc de défilement
    sma_metrics = calculate_sma_for_period(df_filtered)
    sma10_text = f"Moyenne Mobile 10: ${sma_metrics['sma10']:.2f}"
    sma20_text = f"Moyenne Mobile 20: ${sma_metrics['sma20']:.2f}"
    sma50_text = f"Moyenne Mobile 50: ${sma_metrics['sma50']:.2f}"

    return fig, realtime, change_text, high_text, low_text, avg_text, daily, period, sma10_text, sma20_text, sma50_text

# Callback for handling the download
@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input("download-button", "n_clicks"),
     Input('time-range-dropdown', 'value')],
    prevent_initial_call=True
)
def download_csv(n_clicks, time_range):
    if not n_clicks:
        return None

    df = load_data()
    
    # Filtrer les données selon la plage de temps sélectionnée
    now = datetime.now(pytz.UTC).astimezone(pytz.timezone('Europe/Paris'))
    if time_range not in ['all', '5years', '1year', 'ytd']:
        cutoff = now - pd.Timedelta(minutes=time_range)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '5years':
        cutoff = now - pd.Timedelta(days=5*365)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '1year':
        cutoff = now - pd.Timedelta(days=365)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == 'ytd':
        cutoff = pd.to_datetime(f"{now.year}-01-01").tz_localize('Europe/Paris')
        df_filtered = df[df['Time'] >= cutoff]
    else:
        df_filtered = df

    if not df_filtered.empty:
        return dcc.send_data_frame(df_filtered.to_csv, "anet_prices.csv", index=False)
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)
