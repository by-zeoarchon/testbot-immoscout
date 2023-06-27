import requests
from bs4 import BeautifulSoup
import sqlite3
import pdfkit

# Datenbankverbindung herstellen
conn = sqlite3.connect('immoscout.db')
c = conn.cursor()

# Tabelle erstellen
c.execute('''CREATE TABLE IF NOT EXISTS angebote
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             anzeigename TEXT UNIQUE,
             ort TEXT,
             dauer TEXT,
             qm INTEGER,
             kaltmiete INTEGER,
             nebenkosten INTEGER,
             einstellungsdatum TEXT,
             enddatum TEXT)''')

# Immoscout URL
ort = 'Berlin'
radius = 10
url = f'https://www.immoscout24.de/Suche/S-T/Wohnung-Miete/Umkreissuche/{ort}/-/{radius}'

# Angebote abrufen
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
angebote = soup.find_all('div', class_='result-list-entry__data')

for angebot in angebote:
    # Anzeigename
    anzeigename = angebot.find('h5', class_='result-list-entry__brand-title').text.strip()
    
    # Ort
    ort = angebot.find('div', class_='result-list-entry__address').text.strip()
    
    # Dauer der Anzeige
    dauer = angebot.find('div', class_='result-list-entry__criteria').find_all('div')[2].text.strip()
    
    # Quadratmeterzahl
    qm = angebot.find('div', class_='result-list-entry__primary-criterion').text.strip().split(' ')[0]
    
    # Kaltmiete
    kaltmiete = angebot.find('div', class_='result-list-entry__primary-criterion').find_all('dd')[1].text.strip().split(' ')[0]
    
    # Nebenkosten
    nebenkosten = angebot.find('div', class_='result-list-entry__primary-criterion').find_all('dd')[2].text.strip().split(' ')[0]
    
    # Einstellungsdatum
    einstellungsdatum = angebot.find('div', class_='result-list-entry__data--einstellungsdatum').text.strip()
    
    # Enddatum
    enddatum = angebot.find('div', class_='result-list-entry__data--enddatum').text.strip()
    
    # In Datenbank speichern
    c.execute("INSERT OR REPLACE INTO angebote (anzeigename, ort, dauer, qm, kaltmiete, nebenkosten, einstellungsdatum, enddatum) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (anzeigename, ort, dauer, qm, kaltmiete, nebenkosten, einstellungsdatum, enddatum))
    
    # Webseite als PDF herunterladen
    pdfkit.from_url(angebot.find('a')['href'], f'{anzeigename}.pdf')

# Datenbankverbindung schließen
conn.commit()
conn.close()
