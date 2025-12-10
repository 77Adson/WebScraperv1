import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px
import json
from scraper.scheduler import run_scrape_once
from scraper.storage import init_db
from scraper.robot_parser import robot_manager
from analyzer import detect_price_changes

# --- URLs to scrape ---
URLS = {
    "Shop A": "https://scrapeme.live/shop/",
    "Shop B": "https://books.toscrape.com/catalogue/category/books_1/index.html",
    "Shop C": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
}

# --- 0. Wczytywanie konfiguracji ---
@st.cache_data
def load_config():
    """Wczytuje konfigurację z pliku config.json."""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

config = load_config()

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

# --- PASEK BOCZNY - KONTROLA SCRAPERA ---
st.sidebar.header("Panel Sterowania Scraperem")

if st.sidebar.button("Utwórz/Zresetuj bazę danych"):
    try:
        init_db()
        st.sidebar.success("Baza danych została pomyślnie zainicjowana!")
        st.cache_data.clear() # Czyści cache, aby wymusić ponowne załadowanie danych
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Błąd inicjalizacji bazy: {e}")

st.sidebar.subheader("Uruchamianie Scrapera")

if st.sidebar.button("Uruchom jednorazowe pobranie"):
    try:
        # Ustawienia robots.txt na podstawie config.json
        if not config.get("respect_robots_txt", True):
            robot_manager.disabled = True
            st.sidebar.info("Sprawdzanie robots.txt jest wyłączone (zgodnie z config.json).")
        else:
            robot_manager.disabled = False
        
        with st.spinner("Trwa pobieranie danych..."):
            run_scrape_once(URLS)

        st.sidebar.success("Jednorazowe pobieranie zakończone!")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Błąd podczas pobierania: {e}")


# --- Konfiguracja powiadomień email ---
st.sidebar.subheader("Powiadomienia Email i Robots.txt")

respect_robots = st.sidebar.checkbox(
    "Respektuj robots.txt",
    value=config.get("respect_robots_txt", True)
)

email_address = st.sidebar.text_input(
    "Adres email do powiadomień",
    value=config.get("email_address", "")
)
alerts_enabled = st.sidebar.checkbox(
    "Włącz powiadomienia",
    value=config.get("alerts_enabled", False)
)

if st.sidebar.button("Zapisz ustawienia"):
    config['respect_robots_txt'] = respect_robots
    config['email_address'] = email_address
    config['alerts_enabled'] = alerts_enabled
    try:
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        st.sidebar.success("Ustawienia zostały zapisane!")
        st.cache_data.clear() # Wyczyść cache, aby odświeżyć konfigurację
    except Exception as e:
        st.sidebar.error(f"Błąd zapisu konfiguracji: {e}")



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
        st.header("Obecne ceny produktów")
        df_ceny = df_filtrowane.sort_values('data_zdarzenia').groupby('kategoria').tail(1)
        fig_ceny = px.bar(
            df_ceny, 
            x='wartosc', 
            y='kategoria', 
            orientation='h', 
            labels={'kategoria': 'Produkt', 'wartosc': 'Obecna cena'},
            title="Ostatnia zarejestrowana cena dla wybranych produktów"
        )
        st.plotly_chart(fig_ceny, use_container_width=True)
    
        st.markdown("---")
        
        st.header("Analiza trendów dla wybranych produktów")
    
        if not wybrana_kategoria:
            st.info("Wybierz co najmniej jeden produkt z filtrów powyżej, aby zobaczyć analizę trendu.")
        else:
            # Uruchom analizę zmian cen
            # Konwersja DataFrame do formatu listy krotek oczekiwanego przez analyzer
            history_list = [tuple(row) for row in df_filtrowane[['kategoria', 'wartosc', 'region', 'data_zdarzenia']].to_numpy()]
            price_changes = detect_price_changes(history_list)
    
            for produkt in wybrana_kategoria:
                st.markdown(f"---")
                st.subheader(f"Analiza produktu: {produkt}")
                
                df_produkt = df_filtrowane[df_filtrowane['kategoria'] == produkt]
                
                if df_produkt.empty:
                    st.warning(f"Brak danych dla produktu '{produkt}' w wybranym zakresie.")
                    continue
    
                col_info, col_chart = st.columns([1, 2])
    
                with col_info:
                    # Obliczanie statystyk
                    aktualna_cena = df_produkt.sort_values('data_zdarzenia')['wartosc'].iloc[-1]
                    najwyzsza_cena = df_produkt['wartosc'].max()
                    najnizsza_cena = df_produkt['wartosc'].min()
                    
                    st.metric("Aktualna cena", f"{aktualna_cena:,.2f} PLN")
                    st.metric("Najniższa cena w okresie", f"{najnizsza_cena:,.2f} PLN")
                    st.metric("Najwyższa cena w okresie", f"{najwyzsza_cena:,.2f} PLN")
                    
                    # Informacje z analizatora
                    zmiana_procentowa = price_changes.get(produkt)
                    if zmiana_procentowa is not None:
                        st.metric(
                            label="Zmiana ceny w okresie",
                            value=f"{zmiana_procentowa:.1f}%",
                            delta=f"{zmiana_procentowa:.1f}%"
                        )
                    else:
                        st.info("Brak znaczących zmian cen w wybranym okresie.")
    
                with col_chart:
                    # Wykres trendu dla pojedynczego produktu
                    fig_produkt = px.line(
                        df_produkt,
                        x='data_zdarzenia',
                        y='wartosc',
                        title=f"Historia ceny dla: {produkt}",
                        markers=True,
                        labels={'data_zdarzenia': 'Data', 'wartosc': 'Cena'}
                    )
                    fig_produkt.update_xaxes(tickformat='%Y-%m-%d %H:%M')
                    st.plotly_chart(fig_produkt, use_container_width=True)
    
        st.header("Surowe dane po filtrowaniu")
        st.dataframe(df_filtrowane, use_container_width=True)


        ################################# NOWE SPRINT 5 #############################################
        # --- 5A. EKSPORT DANYCH DO CSV ---
        st.markdown("### Eksport danych")

        if df_filtrowane.empty:
            st.info("Brak danych do eksportu dla wybranych filtrów.")
        else:
            csv_data = df_filtrowane.to_csv(index=False).encode('utf-8')

            st.download_button(
                label="Pobierz przefiltrowane dane jako CSV",
                data=csv_data,
                file_name="filtrowane_dane.csv",
                mime="text/csv",
                use_container_width=True
            )

        if not df_oryginal.empty:
            csv_full = df_oryginal.to_csv(index=False).encode('utf-8')

            st.download_button(
                label="Pobierz CAŁĄ bazę danych jako CSV",
                data=csv_full,
                file_name="pelna_baza.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown("---")
        #######################################################
    
else:
    st.warning("Brak danych do wyświetlenia dla wybranych filtrów. Spróbuj zmienić kryteria filtrowania.")
    if df_oryginal.empty:
        st.info("Wygląda na to, że baza danych jest pusta. Uruchom najpierw scraper, aby zebrać dane.")
