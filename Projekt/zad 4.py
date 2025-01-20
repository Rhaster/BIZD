import oracledb
import pandas as pd
import matplotlib.pyplot as plt

DB_USERNAME = "deptulap"
DB_PASSWORD = "Szoner"
DB_DSN = "213.184.8.44:1521/orcl"

def pobierz_kursy_waluty(kod_waluty):
    connection = oracledb.connect(user=DB_USERNAME, password=DB_PASSWORD, dsn=DB_DSN)
    try:
        with connection.cursor() as cursor:
            # Wywołanie funkcji `pobierz_kursy_waluty`, zwracającej SYS_REFCURSOR
            ref_cursor = cursor.callfunc("pobierz_kursy_waluty", oracledb.CURSOR, [kod_waluty])
            
            # Sprawdzenie, czy kursor nie jest `None`
            if ref_cursor is None:
                print("Błąd: `pobierz_kursy_waluty` zwróciło `None`.")
                return pd.DataFrame()  # Zwracamy pusty DataFrame, aby uniknąć błędów

            # Pobranie wyników kursora
            kursy_waluty = ref_cursor.fetchall()

            # Konwersja wyników na DataFrame
            df = pd.DataFrame(kursy_waluty, columns=["Kod Waluty", "Kurs", "Data Operacji", "Źródło"])
            
            # Konwersja daty na format pandas
            df["Data Operacji"] = pd.to_datetime(df["Data Operacji"], format="%d/%m/%y")
            
            # Sortowanie po dacie (dla poprawnego rysowania wykresu)
            df = df.sort_values(by="Data Operacji")
            
            return df
    except Exception as e:
        print(f"Błąd podczas pobierania kursów walut: {e}")
        return pd.DataFrame()  # Zwracamy pusty DataFrame w przypadku błędu

# 📌 Pobranie kursów dla USD

Waluta = "EUR"
df_kursy = pobierz_kursy_waluty(Waluta)

# 📌 Sprawdzenie, czy pobrano dane
if df_kursy.empty:
    print("Brak danych do wyświetlenia.")
else:
    # 📌 Wykres kursów walut w czasie
    plt.figure(figsize=(10, 5))
    plt.plot(df_kursy["Data Operacji"], df_kursy["Kurs"], marker="o", linestyle="-", label=f"Kurs {Waluta}")
    plt.xlabel("Data")
    plt.ylabel("Kurs")
    plt.title(f"Zmiana kursu {Waluta} w czasie")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)

    # 📌 Wyświetlenie wykresu
    plt.show()