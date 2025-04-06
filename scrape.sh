#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
echo "Script exécuté à $(date)" >> "$SCRIPT_DIR/debug.log"

html=$(/usr/bin/curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" https://finviz.com/quote.ashx?t=ANET)
if [ -z "$html" ]; then
    echo "Erreur : curl n'a rien retourné" >> "$SCRIPT_DIR/debug.log"
    exit 1
fi
echo "HTML reçu : ${html:0:100}" >> "$SCRIPT_DIR/debug.log"

price=$(echo "$html" | grep -o '<strong class="quote-price_wrapper_price">[^<]*' | sed 's/.*">//' | head -1)
if [ -z "$price" ]; then
    echo "Erreur : prix non extrait, possible changement de structure HTML" >> "$SCRIPT_DIR/debug.log"
    exit 1
fi
echo "Prix extrait : $price" >> "$SCRIPT_DIR/debug.log"

TIMESTAMP=$(date --iso-8601=seconds)
echo "$TIMESTAMP,$price" >> "$SCRIPT_DIR/recent_prices.csv"
