

import requests
import oracledb
import schedule
from datetime import datetime
import os 
import csv
import time
# Api daje rzadko update, pisze funkcje lekko zmieniajaca kurs za kazdym razem 
import random

# API i baza danych
API_URL = "https://v6.exchangerate-api.com/v6/cf355cbe15343f15ca47c65c/latest/USD"
DB_USERNAME = "deptulap"
DB_PASSWORD = "Szoner"
DB_DSN = "213.184.8.44:1521/orcl"
# folder do zapisu danych 
ARCHIVE_FOLDER = "wyslane_dane"

# Upewnij się, że folder archiwum istnieje
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)
# pobierz dane z API
def fetch_exchange_rates():
    """Pobiera dane o kursach walut z API."""
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        if data["result"] == "success":
            return data["conversion_rates"]
        else:
            raise Exception("API zwróciło błąd: " + data.get("error-type", "Nieznany błąd"))
    else:
        raise Exception(f"Nie udało się połączyć z API. Status code: {response.status_code}")
def archive_to_csv(conversion_rates):
    """Archiwizuje dane do pliku CSV."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(ARCHIVE_FOLDER, f"archiwum_{timestamp}.csv")

    with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Kod Waluty", "Kurs", "Data Archiwizacji"])
        for currency, rate in conversion_rates.items():
            writer.writerow([currency, rate, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    print(f"Dane zostały zarchiwizowane w pliku: {file_path}")
def save_to_oracle(conversion_rates):
    """Ładuje dane do bazy i archiwizuje stare."""
    connection = None
    try:
        # Połączenie z bazą danych
        connection = oracledb.connect(user=DB_USERNAME, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = connection.cursor()

        # Archiwizacja w bazie 
        cursor.execute("""
            INSERT INTO archiwum_kursow_walut (kod_waluty, kurs)
            SELECT kod_waluty, kurs FROM kursy_walut1
        """)
        cursor.execute("DELETE FROM kursy_walut1")
        # Zapis do csv
        archive_to_csv(conversion_rates)
        # Ładowanie nowych danych
        for currency, rate in conversion_rates.items():
            cursor.execute("""
                INSERT INTO kursy_walut1 (kod_waluty, kurs, data_aktualizacji)
                VALUES (:currency, :rate, SYSDATE)
            """, {"currency": currency, "rate": rate})
        # dodanie wpisu do logów 
        aktualizacja_data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
        INSERT INTO logi_operacji (typ_logu, wiadomosc_logu, data_utworzenia)
        VALUES ('INFO', 'Zaktualizowano wszystkie kursy walut na dzień: ' || :aktualizacja_data, SYSDATE)
    """, {"aktualizacja_data": aktualizacja_data})
        # Zatwierdzenie transakcji
        connection.commit()
        print(f"{datetime.now()}: Dane zostały załadowane i zarchiwizowane.")

    except oracledb.Error as error:
        print("Błąd podczas zapisywania do bazy:", error)

    finally:
        if connection:
            connection.close()

# funkcja tworzaca zadanie
def daily_task():
    """Codzienne zadanie."""
    try:
        rates = fetch_exchange_rates()
        updated_rates = {
        currency: rate + random.uniform(-0.2, 0.2) for currency, rate in rates.items()
        }
        save_to_oracle(updated_rates)
    except Exception as e:
        print("Błąd:", e)

# Ustawienie zadania o 1
schedule.every().day.at("01:00").do(daily_task)
# Ustawienie zadania co minute
schedule.every().minute.do(daily_task)
daily_task()
while True:
    schedule.run_pending()
    time.sleep(2)


