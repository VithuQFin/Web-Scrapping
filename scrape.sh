#!/bin/bash
echo "Script exécuté à $(date)" >> /home/ubuntu/Web-Scrapping/debug.log
html=$(/usr/bin/curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" https://finviz.com/quote.ashx?t=ANET)
if [ -z "$html" ]; then
    echo "Erreur : curl n'a rien retourné" >> /home/ubuntu/Web-Scrapping/debug.log
else
    echo "HTML reçu : ${html:0:100}" >> /home/ubuntu/Web-Scrapping/debug.log
fi
price=$(echo "$html" | /usr/bin/grep -oP '(?<=<strong class="quote-price_wrapper_price">)[^<]+' | /usr/bin/head -1)
if [ -z "$price" ]; then
    echo "Erreur : prix non extrait" >> /home/ubuntu/Web-Scrapping/debug.log
else
    echo "Prix extrait : $price" >> /home/ubuntu/Web-Scrapping/debug.log
fi
echo "$(date '+%Y-%m-%d %H:%M:%S'),$price" >> /home/ubuntu/Web-Scrapping/prices.txt
