import oracledb
import pandas as pd
import matplotlib.pyplot as plt

DB_USERNAME = "deptulap"
DB_PASSWORD = "Szoner"
DB_DSN = "213.184.8.44:1521/orcl"



try:
    connection = oracledb.connect(user=DB_USERNAME, password=DB_PASSWORD, dsn=DB_DSN)
    cursor = connection.cursor()
    print("✅ Połączenie z bazą danych nawiązane pomyślnie.")
except Exception as e:
    print("❌ Błąd połączenia z bazą danych:", str(e))
    exit()

# 🔹 ID_LISTA_ZESTAWIEN do filtrowania wyników
ID_LISTA_ZESTAWIEN = 3  # Możesz zmienić wartość według potrzeb

# 🔹 Zapytanie SQL do pobrania danych
sql_query = """
SELECT kod_waluty, sredni_kurs, najnizszy_kurs, najwyzszy_kurs
FROM zestawienia
WHERE id_lista_zestawien = :id_lista_zestawien
ORDER BY kod_waluty
FETCH FIRST 40 ROWS ONLY
"""

# 🔹 Wykonanie zapytania
try:
    cursor.execute(sql_query, [ID_LISTA_ZESTAWIEN])
    rows = cursor.fetchall()

    if not rows:
        print(" Brak danych dla podanego ID_LISTA_ZESTAWIEN.")
        exit()

    # 🔹 Tworzenie DataFrame z wyników zapytania
    df = pd.DataFrame(rows, columns=["Kod Waluty", "Średni Kurs", "Najniższy Kurs", "Najwyższy Kurs"])

    # 🔹 Zamknięcie połączenia
    cursor.close()
    connection.close()
    print(" Pobranie danych zakończone pomyślnie.")

except Exception as e:
    print(" Błąd pobierania danych:", str(e))
    exit()

# 🔹 Generowanie wykresu
plt.figure(figsize=(12, 6))
bar_width = 0.3
x_labels = df["Kod Waluty"]

plt.bar(x_labels, df["Najniższy Kurs"], bar_width, label="Najniższy kurs", alpha=0.7)
plt.bar(x_labels, df["Średni Kurs"], bar_width, label="Średni kurs", alpha=0.7, bottom=df["Najniższy Kurs"])
plt.bar(x_labels, df["Najwyższy Kurs"], bar_width, label="Najwyższy kurs", alpha=0.7, bottom=df["Średni Kurs"])

plt.xlabel("Kod Waluty")
plt.ylabel("Wartość Kursu")
plt.title("Porównanie Najniższych, Średnich i Najwyższych Kursów Walut")
plt.xticks(rotation=45)
plt.legend()
plt.show()