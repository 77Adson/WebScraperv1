import streamlit as st
import pandas as pd
from pathlib import Path

# --- 1. Konfiguracja Strony (Element Sprintu 1) ---
# Ustawiamy podstawowe informacje o naszej aplikacji
st.set_page_config(
    page_title="Panel Danych (Sprint 1)",
    page_icon="📊",  # Prosta ikona
    layout="wide"  # Używamy szerokiego layoutu dla lepszego widoku
)

# --- 2. Wczytywanie Danych (Element Sprintu 1) ---
# Zamiast danych "mockowych", wczytujemy dane z pliku CSV, który jest wynikiem działania backendu.
# Funkcja @st.cache_data zapewnia, że dane wczytają się tylko raz.
@st.cache_data
def load_data():
    """Wczytuje dane z pliku CSV z backendu."""
    # Zakładamy, że plik z danymi znajduje się w katalogu nadrzędnym w folderze 'data'
    # Używamy pathlib dla bardziej obiektowego i czytelnego podejścia do ścieżek
    data_path = Path(__file__).resolve().parent.parent / "data" / "scraped_data.csv"
    
    if not data_path.exists():
        st.error(f"Plik z danymi nie został znaleziony! Oczekiwano go pod ścieżką: {data_path}")
        st.info("Upewnij się, że backend (scraper) zapisał dane w odpowiednim miejscu.")
        # Zwracamy pusty DataFrame, aby uniknąć błędów w dalszej części aplikacji
        return pd.DataFrame({
            'data_zdarzenia': pd.Series(dtype='datetime64[ns]'),
            'kategoria': pd.Series(dtype='object'),
            'wartosc': pd.Series(dtype='int'),
            'region': pd.Series(dtype='object')
        })

    df = pd.read_csv(data_path)
    # Konwersja kolumn na odpowiednie typy, jeśli to konieczne
    df['data_zdarzenia'] = pd.to_datetime(df['data_zdarzenia'])
    df['wartosc'] = pd.to_numeric(df['wartosc'])
    return df.sort_values(by='data_zdarzenia') # Sortujemy dane po dacie

df_oryginal = load_data()

# --- 3. Pasek Boczny z Filtrami (Element Sprintu 1) ---
st.sidebar.header("Filtry Panelu")

# Filtr 1: Wybór kategorii (Selectbox)
if not df_oryginal.empty:
    # Pobieramy unikalne kategorie z danych
    wszystkie_kategorie = df_oryginal['kategoria'].unique()
    # Dodajemy opcję "Wszystkie", aby móc wyłączyć filtr
    opcje_kategorii = ['Wszystkie'] + list(wszystkie_kategorie)
else:
    opcje_kategorii = ['Wszystkie']


wybrana_kategoria = st.sidebar.selectbox(
    "Wybierz kategorię:",
    options=opcje_kategorii
)

# Filtr 2: Zakres wartości (Slider)
if not df_oryginal.empty:
    min_val = int(df_oryginal['wartosc'].min())
    max_val = int(df_oryginal['wartosc'].max())
else:
    min_val, max_val = 0, 1000


zakres_wartosci = st.sidebar.slider(
    "Wybierz zakres wartości:",
    min_value=min_val,
    max_value=max_val,
    value=(min_val, max_val)
)


# --- 4. Logika Filtrowania i Główny Panel (Element Sprintu 1) ---

# Tytuł aplikacji
st.title("📊 Panel Danych - Realizacja Sprintu 1")
st.markdown("To jest podstawowa wersja panelu (MVP) pokazująca kluczowe funkcjonalności Streamlight.")

# Tworzymy kopię danych do filtrowania
df_filtrowane = df_oryginal.copy()

# Aplikowanie filtra kategorii
if wybrana_kategoria != 'Wszystkie':
    df_filtrowane = df_filtrowane[df_filtrowane['kategoria'] == wybrana_kategoria]

# Aplikowanie filtra wartości
df_filtrowane = df_filtrowane[
    (df_filtrowane['wartosc'] >= zakres_wartosci[0]) &
    (df_filtrowane['wartosc'] <= zakres_wartosci[1])
]

# --- 5. Wyświetlanie Wyników (Element Sprintu 1) ---

st.header("Kluczowe Wskaźniki (KPIs)")
# Używamy kolumn do ładnego wyświetlenia metryk
col1, col2, col3 = st.columns(3)
if not df_filtrowane.empty:
    col1.metric("Liczba rekordów", len(df_filtrowane))
    col2.metric("Łączna wartość", f"{df_filtrowane['wartosc'].sum():,} PLN")
    col3.metric("Średnia wartość", f"{df_filtrowane['wartosc'].mean():.2f} PLN")
else:
    col1.metric("Liczba rekordów", 0)
    col2.metric("Łączna wartość", "0 PLN")
    col3.metric("Średnia wartość", "0.00 PLN")

# Wyświetlanie prostego wykresu
st.header("Wykres wartości w czasie")
if not df_filtrowane.empty:
    # Agregujemy dane, aby wykres był czytelny
    df_wykres = df_filtrowane.groupby('data_zdarzenia')['wartosc'].sum()
    st.line_chart(df_wykres)
else:
    st.warning("Brak danych do wyświetlenia dla wybranych filtrów.")

# Wyświetlanie surowych danych (tabeli)
st.header("Surowe dane po filtrowaniu")
st.dataframe(df_filtrowane, use_container_width=True)


# --- Instrukcja uruchomienia ---
st.sidebar.info(
    "**Jak uruchomić ten panel?**\n"
    "1. Zapisz ten kod jako plik, np. `panel.py`.\n"
    "2. Upewnij się, że masz zainstalowane biblioteki:\n"
    "   `pip install streamlit pandas`\n"
    "3. W terminalu uruchom polecenie:\n"
    "   `streamlit run panel.py`"
)