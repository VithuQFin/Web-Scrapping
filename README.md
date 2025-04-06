# Projet de Web Scraping - ANET (Finviz)

Ce projet scrape les prix de l'action ANET(Arista Networks sur Finviz et affiche les données dans un tableau de bord interactif construit avec Dash.

## Fonctionnalités
- Scraping des prix toutes les 5 minutes via un script bash (`scrape.sh`).
- Stockage des données dans historical_prices.csv (ajout de notre part pour enrichir le graphique) et des données récentes dans recent_prices (donner scrappées toutes les 5 minutes avec crontab -e).
- Tableau de bord Dash (`app.py`) affichant :
  - Un graphique des prix au fil du temps avec une moyenne mobile SMA personnalisable.
  - Un rapport quotidien (prix d'ouverture, prix de clôture, moyenne, volatilité, performance).
  - Un rapport de période (basé sur une plage de dates sélectionnée, incluant prix d'ouverture, prix de clôture, volatilité, performance).
  - Statistiques globales (prix minimum, maximum, moyen, volatilité).
  - Le prix en temps réel avec le pourcentage de changement.
  - Possibilité de télécharger les données filtrées au format CSV.
-Mise à jour automatique toutes les 5 minutes via un composant dcc.Interval.

## Prérequis
- Python 3.12
- Git
- Une instance EC2 (facultatif, si tableau de bord en ligne)
- `curl` (pour le script bash)
- Cron (pour automatiser le scraping)

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
- scrape.sh : Script bash pour scraper les prix sur Finviz et les enregistrer dans prices.txt et recent_prices.csv.
- app.py : Tableau de bord Dash pour afficher les données, incluant le graphique, les rapports, et les statistiques.
- historical_prices.csv : Fichier CSV contenant les données historiques des prix.
- recent_prices.csv : Fichier CSV contenant les données récentes des prix, mises à jour toutes les 5 minutes.
- prices.txt : Fichier texte contenant les prix scrapés bruts, utilisé comme source intermédiaire.
- dashboard.log : Logs générés par l'application Dash, utiles pour le débogage.
- debug.log : Logs de débogage pour scrape.sh.
- cron.log : Logs pour la tâche cron.
- nohup.out : Fichier de sortie généré lors de l'exécution de app.py en arrière-plan.
- requirements.txt : Liste des dépendances Python nécessaires pour le projet.
- historicaldata.py : Script probable pour la gestion ou la récupération des données historiques.
- .gitignore : Fichier pour ignorer certains fichiers/dossiers lors des commits Git.
- source/ : Dossier pouvant contenir des scripts ou fichiers sources supplémentaires.
- venv/ : Dossier de l'environnement virtuel Python.

## Auteurs
- Vithusan KAILASAPILLAI
- Rudy LOGGHE



