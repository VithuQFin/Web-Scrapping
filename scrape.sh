#!/bin/bash

echo "Script exécuté à $(date)" >> /home/ec2-user/Web-Scrapping/debug.log
html=$(/usr/bin/curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" https://finviz.com/quote.ashx?t=ANET)
if [ -z "$html" ]; then
    echo "Erreur : curl n'a rien retourné" >> /home/ec2-user/Web-Scrapping/debug.log
else
    echo "HTML reçu : ${html:0:100}" >> /home/ec2-user/Web-Scrapping/debug.log
fi
price=$(echo "$html" | /usr/bin/grep -oP '(?<=<strong class="quote-price_wrapper_price">)[^<]+' | /usr/bin/head -1)
if [ -z "$price" ]; then
    echo "Erreur : prix non extrait" >> /home/ec2-user/Web-Scrapping/debug.log
else
    echo "Prix extrait : $price" >> /home/ec2-user/Web-Scrapping/debug.log
fi
echo "$(date '+%Y-%m-%d %H:%M:%S'),$price" >> /home/ec2-user/Web-Scrapping/prices.txt

SCRIPT_DIR=$(dirname "$(realpath "$0")")
echo "Script exécuté à $(date)" >> "$SCRIPT_DIR/debug.log"
html=$(/usr/bin/curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" https://finviz.com/quote.ashx?t=ANET)
if [ -z "$html" ]; then
    echo "Erreur : curl n'a rien retourné" >> "$SCRIPT_DIR/debug.log"
else
    echo "HTML reçu : ${html:0:100}" >> "$SCRIPT_DIR/debug.log"
fi
price=$(echo "$html" | /usr/bin/grep -oP '(?<=<strong class="quote-price_wrapper_price">)[^<]+' | /usr/bin/head -1)
if [ -z "$price" ]; then
    echo "Erreur : prix non extrait" >> "$SCRIPT_DIR/debug.log"
else
    echo "Prix extrait : $price" >> "$SCRIPT_DIR/debug.log"
    TIMESTAMP=$(date --iso-8601=seconds)
    echo "$TIMESTAMP,$price" >> "$SCRIPT_DIR/recent_prices.csv"
fi
