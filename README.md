# Projet de Web Scraping - ANET (Finviz)

Ce projet scrape les prix de l'action ANET sur Finviz et affiche les données dans un tableau de bord Dash.

## Fonctionnalités
- Scraping des prix toutes les 5 minutes via un script bash (`scrape.sh`).
- Stockage des données dans `prices.txt`.
- Tableau de bord Dash (`app.py`) affichant :
  - Un graphique des prix au fil du temps.
  - Un rapport quotidien (prix d'ouverture, prix de clôture, volatilité, évolution).
  - Le prix en temps réel.

## Prérequis
- Python 3.12
- Git
- Une instance EC2 (facultatif, si tableau de bord en ligne)
- `curl` (pour le script bash)

## Installation
1. Clonez le dépôt : git clone https://github.com/votre-utilisateur/web-scrapping.git cd web-scrapping
2. Créez et activez un environnement virtuel : python3 -m venv venv source venv/bin/activate
3. Installez les dépendances : pip install -r requirements.txt
4. Lancez le tableau de bord : nohup python3 app.py &
5. Accédez au tableau de bord à l'adresse : `http://<adresse-ip>:8050` (remplacer `<adresse-ip>` par l'adresse IP de votre machine ou instance EC2).

## Configuration de la Tâche Cron (Optionnel)
Si vous voulez scraper les prix toutes les 5 minutes :
1. Assurez-vous que `scrape.sh` est exécutable : chmod +x scrape.sh
2. Éditez le crontab : crontab -e
3. Ajoutez la ligne suivante pour exécuter `scrape.sh` toutes les 5 minutes : */5 * * * * /chemin/vers/web-scrapping/scrape.sh >> /chemin/vers/web-scrapping/cron.log 2>&1

## Fichiers Principaux
- `scrape.sh` : Script bash pour scraper les prix et les enregistrer dans `prices.txt`.
- `app.py` : Tableau de bord Dash pour afficher les données.
- `prices.txt` : Fichier contenant les données historiques des prix.
- `debug.log` : Logs de débogage pour `scrape.sh`.
- `cron.log` : Logs pour la tâche cron.

## Personnalisation
- Pour changer l'intervalle de mise à jour du tableau de bord, modifiez la ligne suivante dans `app.py` : dcc.Interval(id='interval-component', interval=5601000, n_intervals=0)
Par exemple, pour une mise à jour toutes les minutes, changez `interval=5*60*1000` en `interval=1*60*1000`.
- Pour changer le fuseau horaire, modifiez la ligne suivante dans `app.py` : df['Time'] = pd.to_datetime(df['Time']).dt.tz_localize('UTC').dt.tz_convert('Europe/Paris')
Remplacez `Europe/Paris` par un autre fuseau horaire (par exemple, `America/New_York`).

## Auteurs
- Vithusan KAILASAPILLAI
- Rudy LOGGHE
