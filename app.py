import os
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import pytz
import logging
import dash_bootstrap_components as dbc

# Configuration logging
logging.basicConfig(filename='dashboard.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'])
app.title = "Tableau de Bord de Web Scrapping - Finviz (ANET)"

# Custom CSS to fix dropdown visibility and improve styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Targeting all parts of the dropdown with higher specificity */
            div[class*="Select"] {
                background-color: #4B5563 !important; /* bg-gray-600 */
                color: #E5E7EB !important; /* text-gray-200 */
                border: 1px solid #4B5563 !important;
            }
            div[class*="Select-control"] {
                background-color: #4B5563 !important;
                border: 1px solid #4B5563 !important;
            }
            div[class*="Select-menu-outer"], div[class*="Select-menu"] {
                background-color: #4B5563 !important;
                color: #E5E7EB !important;
            }
            div[class*="Select-option"] {
                background-color: #4B5563 !important;
                color: #E5E7EB !important;
            }
            div[class*="Select-option"]:hover, div[class*="Select-option"][class*="is-focused"] {
                background-color: #374151 !important; /* bg-gray-700 */
                color: #E5E7EB !important;
            }
            div[class*="Select-value-label"], div[class*="Select-placeholder"], div[class*="Select-input"] > input {
                color: #E5E7EB !important;
            }
            .card-content li {
                margin-bottom: 0.5rem; /* Space between list items */
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORICAL_FILE = os.path.join(BASE_DIR, 'historical_prices.csv')
RECENT_FILE = os.path.join(BASE_DIR, 'recent_prices.csv')

# Cache
cached_data = None
last_cache_time = None
CACHE_DURATION = 290

def load_data():
    global cached_data, last_cache_time
    now = datetime.now()
    if cached_data is not None and last_cache_time is not None:
        if (now - last_cache_time).total_seconds() < CACHE_DURATION:
            logging.info("Utilisation du cache")
            return cached_data

    try:
        historical = pd.read_csv(HISTORICAL_FILE)
        historical['Date'] = pd.to_datetime(historical['Date'], utc=True)
        historical = historical.rename(columns={'Date': 'Time', 'Price': 'Price'})
        historical['Price'] = pd.to_numeric(historical['Price'], errors='coerce')
        logging.info(f"Données historiques chargées : {historical.head()}")
    except Exception as e:
        logging.error(f"Erreur chargement historique : {e}")
        historical = pd.DataFrame(columns=['Time', 'Price'])

    try:
        recent = pd.read_csv(RECENT_FILE, names=['Time', 'Price'])
        recent['Time'] = pd.to_datetime(recent['Time'], utc=True)
        recent['Price'] = pd.to_numeric(recent['Price'], errors='coerce')
        logging.info(f"Données récentes chargées : {recent.head()}")
    except Exception as e:
        logging.error(f"Erreur chargement récent : {e}")
        recent = pd.DataFrame(columns=['Time', 'Price'])

    combined = pd.concat([historical, recent], ignore_index=True).sort_values('Time')
    if not combined.empty:
        combined['Time'] = combined['Time'].dt.tz_convert('Europe/Paris')
        combined = combined[combined['Price'].notna() & (combined['Price'] > 0)]
        logging.info(f"Données combinées : {combined.head()}")
    else:
        logging.warning("Aucune donnée valide après combinaison")

    cached_data = combined
    last_cache_time = now
    return combined

def is_market_closed(date):
    return date.weekday() >= 5

def get_last_market_day(date):
    current_date = date
    while is_market_closed(current_date):
        current_date -= timedelta(days=1)
    return current_date

def daily_report(df, selected_date=None):
    if df.empty:
        return [html.P("Aucune donnée disponible pour le rapport quotidien.")], 0.0
    
    if selected_date is None:
        selected_date = datetime.now(pytz.timezone('Europe/Paris')).date()
    else:
        selected_date = pd.to_datetime(selected_date).date()

    if is_market_closed(selected_date):
        last_market_date = get_last_market_day(selected_date)
        df_date = df[df['Time'].dt.date == last_market_date]
        if df_date.empty:
            return [html.P(f"Aucune donnée pour le dernier jour de marché ({last_market_date.strftime('%Y-%m-%d')}).")], 0.0
        report = [
            html.P(f"Marché fermé le {selected_date.strftime('%Y-%m-%d')} (week-end)."),
            html.P(f"Dernier rapport disponible ({last_market_date.strftime('%Y-%m-%d')}) :")
        ]
    else:
        df_date = df[df['Time'].dt.date == selected_date]
        report = [html.P(f"Rapport Quotidien ({selected_date.strftime('%Y-%m-%d')}) :")]

    if df_date.empty:
        return [html.P(f"Aucune donnée pour le {selected_date.strftime('%Y-%m-%d')}.")], 0.0

    open_price = df_date.iloc[0]['Price']
    close_price = df_date.iloc[-1]['Price']
    volatility = (df_date['Price'].max() - df_date['Price'].min()) / df_date['Price'].mean() * 100
    performance = (close_price - open_price) / open_price * 100
    avg_price = df_date['Price'].mean()

    report.append(html.Ul([
        html.Li(f"Prix d'ouverture : ${open_price:.2f}"),
        html.Li(f"Prix de clôture : ${close_price:.2f}"),
        html.Li(f"Moyenne : ${avg_price:.2f}"),
        html.Li(f"Volatilité : {volatility:.2f}%"),
        html.Li(f"Performance : {performance:.2f}%")
    ], className="card-content"))

    return report, performance

def period_report(df_filtered):
    if df_filtered.empty:
        return [html.P("Aucune donnée pour la période sélectionnée.")], 0.0
    
    open_price = df_filtered.iloc[0]['Price']
    close_price = df_filtered.iloc[-1]['Price']
    volatility = (df_filtered['Price'].max() - df_filtered['Price'].min()) / df_filtered['Price'].mean() * 100
    performance = (close_price - open_price) / open_price * 100

    report = html.Ul([
        html.Li(f"Prix d'ouverture : ${open_price:.2f}"),
        html.Li(f"Prix de clôture : ${close_price:.2f}"),
        html.Li(f"Volatilité : {volatility:.2f}%"),
        html.Li(f"Performance : {performance:.2f}%")
    ], className="card-content")

    return [report], performance

def get_latest_price_and_change(df):
    if df.empty:
        return "Prix en temps réel indisponible.", 0.0
    latest_price = df.iloc[-1]['Price']
    previous_price = df.iloc[-2]['Price'] if len(df) > 1 else latest_price
    price_change = 0.0
    if previous_price != 0:  # Avoid division by zero
        price_change = (latest_price - previous_price) / previous_price * 100
    return f"Prix actuel de ANET : ${latest_price:.2f} (à {df.iloc[-1]['Time'].strftime('%Y-%m-%d %H:%M:%S')})", price_change

def get_price_stats(df):
    if df.empty:
        return {"min": 0, "max": 0, "avg": 0, "volatility": 0}
    
    min_price = df['Price'].min()
    max_price = df['Price'].max()
    avg_price = df['Price'].mean()
    volatility = (max_price - min_price) / avg_price * 100 if avg_price > 0 else 0

    return {
        "min": min_price,
        "max": max_price,
        "avg": avg_price,
        "volatility": volatility
    }

# Define the block content for fixed layout
block_content = [
    # Real-Time Price Card
    html.Div([
        html.H2("Prix en Temps Réel", className="text-lg font-semibold text-gray-200 mb-2"),
        html.H3(id='realtime-price', className="text-xl font-bold text-green-400"),
        html.P(id='price-change', className="text-sm mt-2"),
    ], className="bg-gray-700 p-4 rounded-lg shadow-md flex-1 mx-2 min-w-[200px]"),

    # Global Statistics Card
    html.Div([
        html.H2("Statistiques Globales", className="text-lg font-semibold text-gray-200 mb-2"),
        html.Ul([
            html.Li(id='price-stats-min', className="text-gray-400"),
            html.Li(id='price-stats-max', className="text-gray-400"),
            html.Li(id='price-stats-avg', className="text-gray-400"),
            html.Li(id='price-stats-volatility', className="text-gray-400"),
        ], className="card-content")
    ], className="bg-gray-700 p-4 rounded-lg shadow-md flex-1 mx-2 min-w-[200px]"),

    # Daily Report Card
    html.Div([
        html.H2("Rapport Quotidien", className="text-lg font-semibold text-gray-200 mb-2"),
        dcc.DatePickerSingle(id='report-date-picker', date=datetime.now().date(), display_format='YYYY-MM-DD', className="mb-3 p-2 rounded bg-gray-600 text-gray-200 w-full"),
        html.Div(id='daily-report', className="text-gray-400"),
        html.Span(id='evolution-badge', className="text-sm mt-2"),
    ], className="bg-gray-700 p-4 rounded-lg shadow-md flex-1 mx-2 min-w-[200px]"),

    # Period Report Card
    html.Div([
        html.H2("Rapport de Période", className="text-lg font-semibold text-gray-200 mb-2"),
        dcc.DatePickerRange(id='period-date-picker', start_date=datetime(2025, 1, 1).date(), end_date=datetime.now().date(), display_format='YYYY-MM-DD', className="mb-3 p-2 rounded bg-gray-600 text-gray-200 w-full"),
        html.Div(id='period-report', className="text-gray-400"),
        html.Span(id='period-evolution-badge', className="text-sm mt-2"),
    ], className="bg-gray-700 p-4 rounded-lg shadow-md flex-1 mx-2 min-w-[200px]"),
]

app.layout = html.Div([
# Header
html.Div([
    html.H1("Tableau de Bord de Web Scrapping - Finviz (ANET | Arista Networks)", className="text-3xl font-bold text-gray-200 text-center mb-4"),
    html.P("Suivi en temps réel des prix de ANET via Finviz", className="text-lg text-gray-400 text-center mb-2"),
    html.P("Réalisé par Vithusan KAILASAPILLAI et Rudy LOGGHE", className="text-md text-gray-300 text-center mb-6")
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
                    {'label': '3 Ans', 'value': '3years'},
                    {'label': '1 An', 'value': '1year'},
                    {'label': 'YTD', 'value': 'ytd'},
                    {'label': '6 Mois', 'value': '6months'},
                    {'label': '3 Mois', 'value': '3months'},
                    {'label': '1 Mois', 'value': '1month'},
                    {'label': '1 Semaine', 'value': '1week'},
                    {'label': '1 Jour', 'value': 1440},
                    {'label': '1 heure', 'value': 60},
                    {'label': '30 minutes', 'value': 30},
                    {'label': '10 minutes', 'value': 10},
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
                value=50,
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
     Output('price-stats-min', 'children'),
     Output('price-stats-max', 'children'),
     Output('price-stats-avg', 'children'),
     Output('price-stats-volatility', 'children'),
     Output('daily-report', 'children'),
     Output('evolution-badge', 'children'),
     Output('period-report', 'children'),
     Output('period-evolution-badge', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('time-range-dropdown', 'value'),
     Input('sma-period-dropdown', 'value'),
     Input('report-date-picker', 'date'),
     Input('period-date-picker', 'start_date'),
     Input('period-date-picker', 'end_date')]
)
def update_dashboard(n, time_range, sma_period, report_date, period_start_date, period_end_date):
    df = load_data()
    if df.empty:
        return ({}, "Prix indisponible", "", "N/A", "N/A", "N/A", "N/A", [html.P("Aucune donnée disponible.")], "", [html.P("Aucune donnée disponible.")], "")

    # Filter data for graph
    now = datetime.now(pytz.timezone('Europe/Paris'))
    if time_range not in ['all', '5years', '3years', '1year', 'ytd', '6months', '3months', '1month', '1week']:
        cutoff = now - pd.Timedelta(minutes=time_range)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '5years':
        cutoff = now - pd.Timedelta(days=5*365)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '3years':
        cutoff = now - pd.Timedelta(days=3*365)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '1year':
        cutoff = now - pd.Timedelta(days=365)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == 'ytd':
        cutoff = pd.to_datetime(f"{now.year}-01-01").tz_localize('Europe/Paris')
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '6months':
        cutoff = now - pd.Timedelta(days=180)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '3months':
        cutoff = now - pd.Timedelta(days=90)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '1month':
        cutoff = now - pd.Timedelta(days=30)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '1week':
        cutoff = now - pd.Timedelta(days=7)
        df_filtered = df[df['Time'] >= cutoff]
    else:
        df_filtered = df
    
    df_filtered = df_filtered.sort_values('Time')

    # Calculate SMA for graph
    sma_label = f"SMA_{sma_period}"
    df_filtered[sma_label] = df_filtered['Price'].rolling(window=sma_period, min_periods=1).mean()

    # Create graph
    fig = px.line(df_filtered, x='Time', y=['Price', sma_label],
                  labels={'value': 'Prix ($)', 'variable': 'Ligne'},
                  title='Évolution de ANET (Scraping toutes les 5 minutes)')
    fig.update_layout(
        plot_bgcolor='#374151',  # bg-gray-700
        paper_bgcolor='#374151',  # bg-gray-700
        font_color='#E5E7EB',  # text-gray-200
        title_font_color='#E5E7EB',
        xaxis_gridcolor='#4B5563',  # bg-gray-600
        yaxis_gridcolor='#4B5563',
        title_font_size=20,
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode='x unified',
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),  # Disable the rangeslider
            type='date'
        )
    )
    fig.update_traces(line_width=3, line_color='#2563EB', selector=dict(name='Price'))  # Thicker line for Price
    fig.update_traces(line_width=1.5, line_dash='dash', line_color='#F97316', opacity=0.7, selector=dict(name=sma_label))  # Thinner, dashed, semi-transparent line for SMA

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
            font=dict(color='#E5E7EB')
        )

    # Real-time price and change
    realtime, change = get_latest_price_and_change(df)
    change_text = f"Changement: {'+' if change >= 0 else ''}{change:.2f}%"
    change_color = "text-green-400" if change >= 0 else "text-red-400"
    change_text = html.Span(change_text, className=change_color)

    # Global statistics
    stats = get_price_stats(df_filtered)
    min_text = f"Prix Minimum: ${stats['min']:.2f}"
    max_text = f"Prix Maximum: ${stats['max']:.2f}"
    avg_text = f"Prix Moyen: ${stats['avg']:.2f}"
    volatility_text = f"Volatilité: {stats['volatility']:.2f}%"

    # Daily report
    daily_rep, daily_perf = daily_report(df, report_date)
    daily_badge = f"Performance: {'+' if daily_perf >= 0 else ''}{daily_perf:.2f}%"
    daily_badge_color = "text-green-400" if daily_perf >= 0 else "text-red-400"
    daily_badge = html.Span(daily_badge, className=daily_badge_color)

    # Period report
    period_start_date = pd.to_datetime(period_start_date).date()
    period_end_date = pd.to_datetime(period_end_date).date()
    df_period = df[(df['Time'].dt.date >= period_start_date) & (df['Time'].dt.date <= period_end_date)]
    period_rep, period_perf = period_report(df_period)
    period_badge = f"Performance: {'+' if period_perf >= 0 else ''}{period_perf:.2f}%"
    period_badge_color = "text-green-400" if period_perf >= 0 else "text-red-400"
    period_badge = html.Span(period_badge, className=period_badge_color)

    return (fig, realtime, change_text, min_text, max_text, avg_text, volatility_text, daily_rep, daily_badge, period_rep, period_badge)

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
    
    # Filter data based on selected time range
    now = datetime.now(pytz.timezone('Europe/Paris'))
    if time_range not in ['all', '5years', '3years', '1year', 'ytd', '6months', '3months', '1month', '1week']:
        cutoff = now - pd.Timedelta(minutes=time_range)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '5years':
        cutoff = now - pd.Timedelta(days=5*365)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '3years':
        cutoff = now - pd.Timedelta(days=3*365)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '1year':
        cutoff = now - pd.Timedelta(days=365)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == 'ytd':
        cutoff = pd.to_datetime(f"{now.year}-01-01").tz_localize('Europe/Paris')
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '6months':
        cutoff = now - pd.Timedelta(days=180)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '3months':
        cutoff = now - pd.Timedelta(days=90)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '1month':
        cutoff = now - pd.Timedelta(days=30)
        df_filtered = df[df['Time'] >= cutoff]
    elif time_range == '1week':
        cutoff = now - pd.Timedelta(days=7)
        df_filtered = df[df['Time'] >= cutoff]
    else:
        df_filtered = df

    if not df_filtered.empty:
        return dcc.send_data_frame(df_filtered.to_csv, "anet_prices.csv", index=False)
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)
