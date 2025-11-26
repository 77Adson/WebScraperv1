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
        return df.sort_values(by='data_zdarzenia')
    except Exception as e:
        st.error(f"Wystąpił błąd podczas odczytu danych z bazy SQLite: {e}")
        return pd.DataFrame()


df_oryginal = load_data()

st.subheader("Data loaded from database")
st.dataframe(df_oryginal)

# --- 3. PASEK BOCZNY Z FILTRAMI ---
st.sidebar.header("Opcje Filtrowania")

# Initialize filter variables
wybrany_sklep = None
wybrana_kategoria = []
zakres_dat = (None, None)
zakres_wartosci = (0, 1)

if not df_oryginal.empty:
    # --- Etap 1: Filtr regionu (sklepu) ---
    wszystkie_regiony = sorted(df_oryginal['region'].unique())
    wybrany_sklep = st.sidebar.selectbox(
        "Krok 1: Wybierz sklep",
        options=wszystkie_regiony,
        index=None,
        placeholder="Wybierz sklep, aby zobaczyć produkty..."
    )

    # --- Etap 2: Filtr kategorii (produktów) ---
    if wybrany_sklep:
        df_dla_sklepu = df_oryginal[df_oryginal['region'] == wybrany_sklep]
        kategorie_w_sklepie = sorted(df_dla_sklepu['kategoria'].unique())
        
        wybrana_kategoria = st.sidebar.multiselect(
            "Krok 2: Wybierz produkty (max 10)",
            options=kategorie_w_sklepie,
            max_selections=10
        )
    else:
        st.sidebar.info("Najpierw wybierz sklep, aby włączyć filtrowanie produktów.")

    # --- Pozostałe filtry ---
    min_date = df_oryginal['data_zdarzenia'].dt.date.min()
    max_date = df_oryginal['data_zdarzenia'].dt.date.max()
    zakres_dat = st.sidebar.date_input(
        "Wybierz zakres dat",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        disabled=not wybrany_sklep
    )

    min_val = float(df_oryginal['wartosc'].min())
    max_val = float(df_oryginal['wartosc'].max())
    zakres_wartosci = st.sidebar.slider(
        "Wybierz zakres wartości",
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val),
        disabled=not wybrany_sklep
    )

else:
    st.sidebar.warning("Brak danych do filtrowania.")

# --- 4. LOGIKA FILTROWANIA I GŁÓWNY PANEL ---

st.title("📊 Dashboard Analizy Danych")
st.markdown("Interaktywny panel do wizualizacji danych zebranych przez scraper.")

df_filtrowane = df_oryginal.copy()

# Aplikowanie filtrów - główna logika
# Zaczynamy filtrowanie dopiero po wybraniu sklepu
if wybrany_sklep:
    # 1. Filtr sklepu (regionu)
    df_filtrowane = df_filtrowane[df_filtrowane['region'] == wybrany_sklep]

    # 2. Filtr kategorii (zawsze filtruj wg wybranych)
    df_filtrowane = df_filtrowane[df_filtrowane['kategoria'].isin(wybrana_kategoria)]

    # 3. Filtr daty
    if len(zakres_dat) == 2:
        df_filtrowane = df_filtrowane[
            (df_filtrowane['data_zdarzenia'].dt.date >= zakres_dat[0]) &
            (df_filtrowane['data_zdarzenia'].dt.date <= zakres_dat[1])
        ]

    # 4. Filtr wartości
    df_filtrowane = df_filtrowane[
        (df_filtrowane['wartosc'] >= zakres_wartosci[0]) &
        (df_filtrowane['wartosc'] <= zakres_wartosci[1])
    ]
else:
    # Jeśli żaden sklep nie jest wybrany, df_filtrowane pozostaje puste,
    # aby nie wyświetlać danych, dopóki użytkownik nie dokona wyboru.
    df_filtrowane = pd.DataFrame(columns=df_oryginal.columns)

st.subheader("Data after filtering")
st.dataframe(df_filtrowane)

# --- 5. WYŚWIETLANIE WYNIKÓW ---
if not wybrany_sklep:
    st.info("Proszę wybrać sklep z panelu po lewej stronie, aby rozpocząć analizę.")
elif not df_filtrowane.empty:
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
        # Usunięto grupowanie, aby wyświetlić wszystkie punkty danych
        fig_czas = px.line(
            df_filtrowane,
            x='data_zdarzenia',
            y='wartosc',
            facet_row='kategoria', # Tworzy osobny wiersz z wykresem dla każdej kategorii
            labels={'data_zdarzenia': 'Data', 'wartosc': 'Suma wartości', 'kategoria': 'Kategoria'},
            markers=True # Pokazuje punkty danych, nawet jeśli jest tylko jeden
        )
        # Poprawiamy czytelność, ukrywając tytuły osi Y dla poszczególnych pod-wykresów
        fig_czas.update_yaxes(title_text="")
        # Ustawiamy typ osi X na datę i formatujemy etykiety, aby pokazywały czas
        fig_czas.update_xaxes(tickformat='%Y-%m-%d<br>%H:%M:%S')
        # Dynamiczna wysokość, ale z ograniczeniem, aby nie była zbyt mała
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
    
    # --- Surowe dane ---
    st.header("Surowe dane po filtrowaniu")
    st.dataframe(df_filtrowane, use_container_width=True)
    
else:
    st.warning("Brak danych do wyświetlenia dla wybranych filtrów. Spróbuj zmienić kryteria filtrowania.")
    if df_oryginal.empty:
        st.info("Wygląda na to, że baza danych jest pusta. Uruchom najpierw scraper, aby zebrać dane.")
        
# --- INFORMACJE W PASKU BOCZNYM ---