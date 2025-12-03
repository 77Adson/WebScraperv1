import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px
from scheduler import run_scrape_once, run_scheduler
from storage import init_db

# --- URLs to scrape ---
URLS = {
    "Shop A": "https://scrapeme.live/shop/",
    "Shop B": "https://books.toscrape.com/catalogue/category/books_1/index.html",
    "Shop C": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
}

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
    db_path = Path(__file__).resolve().parent / "scraped_data.db"
    
    if not db_path.exists():
        st.error(f"Plik bazy danych nie został znaleziony! Oczekiwano go pod ścieżką: {db_path}")
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
        return df.sort_values(by='data_zdarzenia')
    except Exception as e:
        st.error(f"Wystąpił błąd podczas odczytu danych z bazy SQLite: {e}")
        return pd.DataFrame()

df_oryginal = load_data()

# --- PASEK BOCZny - KONTROLA SCRAPERA ---
st.sidebar.header("Panel Sterowania Scraperem")

if st.sidebar.button("Utwórz/Zresetuj bazę danych"):
    try:
        init_db()
        st.sidebar.success("Baza danych została pomyślnie zainicjowana!")
        st.cache_data.clear() # Czyści cache, aby wymusić ponowne załadowanie danych
        st.experimental_rerun()
    except Exception as e:
        st.sidebar.error(f"Błąd inicjalizacji bazy: {e}")

st.sidebar.subheader("Uruchamianie Scrapera")

if st.sidebar.button("Uruchom jednorazowe pobranie"):
    try:
        with st.spinner("Trwa pobieranie danych..."):
            run_scrape_once(URLS)
        st.sidebar.success("Jednorazowe pobieranie zakończone!")
        st.cache_data.clear()
        st.experimental_rerun()
    except Exception as e:
        st.sidebar.error(f"Błąd podczas pobierania: {e}")

st.sidebar.subheader("Scraper Cykliczny")
minutes = st.sidebar.number_input(
    "Co ile minut wykonywać pobranie?",
    min_value=1,
    value=60,
    step=1
)

if st.sidebar.button("Uruchom cykliczne pobieranie"):
    try:
        # Uwaga: Streamlit zakończy działanie tego procesu, jeśli aplikacja zostanie zamknięta.
        # To jest uproszczona implementacja.
        with st.spinner(f"Uruchamiam cykliczne pobieranie co {minutes} minut..."):
            run_scheduler(URLS, interval_minutes=minutes)
        st.sidebar.success("Scheduler został uruchomiony.")
        st.info("Pamiętaj, że scheduler działa tylko, gdy ta aplikacja jest aktywna.")
    except Exception as e:
        st.sidebar.error(f"Błąd podczas uruchamiania schedulera: {e}")


st.title("📊 Dashboard Analizy Danych")
st.markdown("Interaktywny panel do wizualizacji danych zebranych przez scraper.")

# --- 3. FILTRY W EXPANDERZE ---
with st.expander("Opcje Filtrowania", expanded=True):
    # Initialize filter variables
    wybrany_sklep = None
    wybrana_kategoria = []
    zakres_dat = (None, None)
    zakres_wartosci = (0, 1)

    if not df_oryginal.empty:
        # --- Etap 1: Filtr regionu (sklepu) ---
        wszystkie_regiony = sorted(df_oryginal['region'].unique())
        wybrany_sklep = st.selectbox(
            "Krok 1: Wybierz sklep",
            options=wszystkie_regiony,
            index=None,
            placeholder="Wybierz sklep, aby zobaczyć produkty..."
        )

        # --- Etap 2: Filtr kategorii (produktów) ---
        if wybrany_sklep:
            df_dla_sklepu = df_oryginal[df_oryginal['region'] == wybrany_sklep]
            kategorie_w_sklepie = sorted(df_dla_sklepu['kategoria'].unique())
            
            wybrana_kategoria = st.multiselect(
                "Krok 2: Wybierz produkty (max 10)",
                options=kategorie_w_sklepie,
                max_selections=10
            )
        else:
            st.info("Najpierw wybierz sklep, aby włączyć filtrowanie produktów.")

        # --- Pozostałe filtry ---
        min_date = df_oryginal['data_zdarzenia'].dt.date.min()
        max_date = df_oryginal['data_zdarzenia'].dt.date.max()
        zakres_dat = st.date_input(
            "Wybierz zakres dat",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            disabled=not wybrany_sklep
        )

        min_val = float(df_oryginal['wartosc'].min())
        max_val = float(df_oryginal['wartosc'].max())
        zakres_wartosci = st.slider(
            "Wybierz zakres wartości",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            disabled=not wybrany_sklep
        )

    else:
        st.warning("Brak danych do filtrowania.")

# --- 4. LOGIKA FILTROWANIA ---
df_filtrowane = df_oryginal.copy()

if wybrany_sklep:
    df_filtrowane = df_filtrowane[df_filtrowane['region'] == wybrany_sklep]
    if wybrana_kategoria:
        df_filtrowane = df_filtrowane[df_filtrowane['kategoria'].isin(wybrana_kategoria)]
    if len(zakres_dat) == 2:
        df_filtrowane = df_filtrowane[
            (df_filtrowane['data_zdarzenia'].dt.date >= zakres_dat[0]) &
            (df_filtrowane['data_zdarzenia'].dt.date <= zakres_dat[1])
        ]
    df_filtrowane = df_filtrowane[
        (df_filtrowane['wartosc'] >= zakres_wartosci[0]) &
        (df_filtrowane['wartosc'] <= zakres_wartosci[1])
    ]
else:
    df_filtrowane = pd.DataFrame(columns=df_oryginal.columns)

# --- 5. WYŚWIETLANIE WYNIKÓW ---
if not wybrany_sklep:
    st.info("Proszę wybrać sklep z panelu po lewej stronie, aby rozpocząć analizę.")
elif not df_filtrowane.empty:
    st.header("Kluczowe Wskaźniki (KPIs)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Liczba Rekordów", f"{len(df_filtrowane):,}")
    col2.metric("Łączna Wartość", f"{df_filtrowane['wartosc'].sum():,.2f} PLN")
    col3.metric("Średnia Wartość", f"{df_filtrowane['wartosc'].mean():,.2f} PLN")
    col4.metric("Liczba Kategorii", df_filtrowane['kategoria'].nunique())
    
    st.markdown("---")
    
    st.header("Wizualizacje Danych")
    fig_col1, fig_col2 = st.columns(2)
    
    with fig_col1:
        st.subheader("Trend wartości w czasie")
        fig_czas = px.line(
            df_filtrowane,
            x='data_zdarzenia',
            y='wartosc',
            facet_row='kategoria',
            labels={'data_zdarzenia': 'Data', 'wartosc': 'Suma wartości', 'kategoria': 'Kategoria'},
            markers=True
        )
        fig_czas.update_yaxes(title_text="")
        fig_czas.update_xaxes(tickformat='%Y-%m-%d<br>%H:%M:%S')
        fig_czas.update_layout(height=max(400, 200 * df_filtrowane['kategoria'].nunique()))
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
    
    st.header("Surowe dane po filtrowaniu")
    st.dataframe(df_filtrowane, use_container_width=True)
    
else:
    st.warning("Brak danych do wyświetlenia dla wybranych filtrów. Spróbuj zmienić kryteria filtrowania.")
    if df_oryginal.empty:
        st.info("Wygląda na to, że baza danych jest pusta. Uruchom najpierw scraper, aby zebrać dane.")
