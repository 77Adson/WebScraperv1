import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Dashboard Analizy Danych",
    page_icon="📊",
    layout="wide"
)

# --- 2. WCZYTYWANIE DANYCH ---
@st.cache_data
def load_data():
    """Wczytuje dane z bazy danych SQLite z backendu."""
    db_path = Path(__file__).resolve().parent.parent / "scraped_data.db"
    
    if not db_path.exists():
        st.error(f"Plik bazy danych nie został znaleziony! Oczekiwano go pod ścieżką: {db_path}")
        st.info("Upewnij się, że backend (scraper) zapisał dane w odpowiednim miejscu.")
        return pd.DataFrame({
            'data_zdarzenia': pd.Series(dtype='datetime64[ns]'),
            'kategoria': pd.Series(dtype='object'),
            'wartosc': pd.Series(dtype='float'),
            'region': pd.Series(dtype='object')
        })
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM scraped_data"
        df = pd.read_sql_query(query, conn, parse_dates=['data_zdarzenia'])
        conn.close()
        df['data_zdarzenia'] = pd.to_datetime(df['data_zdarzenia']).dt.date
        return df.sort_values(by='data_zdarzenia')
    except Exception as e:
        st.error(f"Wystąpił błąd podczas odczytu danych z bazy SQLite: {e}")
        return pd.DataFrame()


df_oryginal = load_data()

# --- 3. PASEK BOCZNY Z FILTRAMI ---
st.sidebar.header("Opcje Filtrowania")

if not df_oryginal.empty:
    # --- Filtr kategorii ---
    wszystkie_kategorie = sorted(df_oryginal['kategoria'].unique())
    wybrana_kategoria = st.sidebar.multiselect(
        "Wybierz kategorię:",
        options=wszystkie_kategorie,
        default=wszystkie_kategorie
    )

    # --- Filtr regionu ---
    wszystkie_regiony = sorted(df_oryginal['region'].unique())
    wybrany_region = st.sidebar.multiselect(
        "Wybierz region:",
        options=wszystkie_regiony,
        default=wszystkie_regiony
    )

    # --- Filtr daty ---
    min_date = df_oryginal['data_zdarzenia'].min()
    max_date = df_oryginal['data_zdarzenia'].max()
    zakres_dat = st.sidebar.date_input(
        "Wybierz zakres dat:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # --- Filtr wartości ---
    min_val = float(df_oryginal['wartosc'].min())
    max_val = float(df_oryginal['wartosc'].max())
    zakres_wartosci = st.sidebar.slider(
        "Wybierz zakres wartości:",
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val)
    )

else:
    st.sidebar.warning("Brak danych do filtrowania.")
    wybrana_kategoria = []
    wybrany_region = []
    zakres_dat = (None, None)
    zakres_wartosci = (0, 1)


# --- 4. LOGIKA FILTROWANIA I GŁÓWNY PANEL ---

st.title("📊 Dashboard Analizy Danych")
st.markdown("Interaktywny panel do wizualizacji danych zebranych przez scraper.")

df_filtrowane = df_oryginal.copy()

# Aplikowanie filtrów, jeśli dane istnieją
if not df_filtrowane.empty and wybrana_kategoria and wybrany_region and len(zakres_dat) == 2:
    df_filtrowane = df_filtrowane[df_filtrowane['kategoria'].isin(wybrana_kategoria)]
    df_filtrowane = df_filtrowane[df_filtrowane['region'].isin(wybrany_region)]
    df_filtrowane = df_filtrowane[
        (df_filtrowane['data_zdarzenia'] >= zakres_dat[0]) &
        (df_filtrowane['data_zdarzenia'] <= zakres_dat[1])
    ]
    df_filtrowane = df_filtrowane[
        (df_filtrowane['wartosc'] >= zakres_wartosci[0]) &
        (df_filtrowane['wartosc'] <= zakres_wartosci[1])
    ]

# --- 5. WYŚWIETLANIE WYNIKÓW ---
if not df_filtrowane.empty:
    # --- Kluczowe wskaźniki (KPIs) ---
    st.header("Kluczowe Wskaźniki (KPIs)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Liczba Rekordów", f"{len(df_filtrowane):,}")
    col2.metric("Łączna Wartość", f"{df_filtrowane['wartosc'].sum():,.2f} PLN")
    col3.metric("Średnia Wartość", f"{df_filtrowane['wartosc'].mean():,.2f} PLN")
    col4.metric("Liczba Kategorii", df_filtrowane['kategoria'].nunique())
    
    st.markdown("---")
    
    # --- Wizualizacje ---
    st.header("Wizualizacje Danych")
    
    # Wykresy w dwóch kolumnach
    fig_col1, fig_col2 = st.columns(2)
    
    with fig_col1:
        st.subheader("Trend wartości w czasie")
        df_wykres_czas = df_filtrowane.groupby('data_zdarzenia')['wartosc'].sum().reset_index()
        fig_czas = px.line(df_wykres_czas, x='data_zdarzenia', y='wartosc', labels={'data_zdarzenia': 'Data', 'wartosc': 'Suma wartości'})
        st.plotly_chart(fig_czas, use_container_width=True)
        
        st.subheader("Rozkład produktów wg kategorii")
        df_wykres_kategorie_pie = df_filtrowane['kategoria'].value_counts().reset_index()
        df_wykres_kategorie_pie.columns = ['kategoria', 'liczba']
        fig_pie_kategoria = px.pie(df_wykres_kategorie_pie, names='kategoria', values='liczba')
        st.plotly_chart(fig_pie_kategoria, use_container_width=True)
        
    with fig_col2:
        st.subheader("Suma wartości wg kategorii")
        df_wykres_kategorie_bar = df_filtrowane.groupby('kategoria')['wartosc'].sum().sort_values(ascending=False).reset_index()
        fig_bar_kategoria = px.bar(df_wykres_kategorie_bar, x='wartosc', y='kategoria', orientation='h', labels={'kategoria': 'Kategoria', 'wartosc': 'Suma wartości'})
        st.plotly_chart(fig_bar_kategoria, use_container_width=True)
        
        st.subheader("Liczba rekordów wg regionu")
        df_wykres_region = df_filtrowane['region'].value_counts().reset_index()
        df_wykres_region.columns = ['region', 'liczba']
        fig_bar_region = px.bar(df_wykres_region, x='liczba', y='region', orientation='h', labels={'region': 'Region', 'liczba': 'Liczba rekordów'})
        st.plotly_chart(fig_bar_region, use_container_width=True)
        
    st.markdown("---")
    
    # --- Surowe dane ---
    st.header("Surowe dane po filtrowaniu")
    st.dataframe(df_filtrowane, use_container_width=True)
    
else:
    st.warning("Brak danych do wyświetlenia dla wybranych filtrów. Spróbuj zmienić kryteria filtrowania.")
    if df_oryginal.empty:
        st.info("Wygląda na to, że baza danych jest pusta. Uruchom najpierw scraper, aby zebrać dane.")
        
# --- INFORMACJE W PASKU BOCZNYM ---
st.sidebar.info(
    "**Jak uruchomić ten panel?**\n"
    "1. Upewnij się, że plik `scraped_data.db` istnieje w głównym katalogu projektu.\n"
    "2. Użyj filtrów, aby dynamicznie analizować dane.\n"
    "3. Aby odświeżyć dane, odśwież stronę w przeglądarce."
)
st.sidebar.markdown("---")
st.sidebar.markdown("Stworzone przy użyciu `Streamlit` & `Plotly`.")