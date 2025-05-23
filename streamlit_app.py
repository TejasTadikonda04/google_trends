# === APP CONFIG ===
import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pycountry
import math
import json
import glob
import unicodedata
import re
from difflib import get_close_matches
from streamlit_plotly_events import plotly_events

st.set_page_config(page_title="Interactive Trends Dashboard", layout="wide")

# === GLOBAL CSS ===
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
  }
  .scroll-panel {
    max-height: 350px;
    overflow-y: auto !important;
    padding: 8px;
    background-color: #1e1e1e;
    border-radius: 6px;
  }
  .scroll-panel table {
    width: 100%;
    border-collapse: collapse;
  }
  .scroll-panel th, .scroll-panel td {
    padding: 6px 8px;
    color: #e0e0e0;
    font-size: 14px;
  }
  .scroll-panel thead th {
    background-color: #2a2a2a;
    position: sticky;
    top: 0;
    z-index: 2;
  }
  .scroll-panel tbody tr:hover {
    background-color: #333;
  }
  .home-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 90vh;
    text-align: center;
  }
  .home-title {
    font-size: 48px;
    font-weight: bold;
    color: #00c4cc;
    margin-bottom: 20px;
    animation: fadein 2s ease-in;
  }
  .home-subtitle {
    font-size: 18px;
    font-weight: 400;
    color: #e0e0e0;
    animation: fadein 2s ease-in;
  }
  @keyframes fadein {
    from { opacity: 0; }
    to   { opacity: 1; }
  }
</style>
""", unsafe_allow_html=True)

# === LATIN SCRIPT COUNTRIES ===
latin_script_countries = [
    'Brazil', 'Belgium', 'United Kingdom', 'Norway', 'Italy', 'Portugal',
    'Netherlands', 'Poland', 'Mexico', 'Nigeria', 'South Africa', 'Austria',
    'Chile', 'Finland', 'Philippines', 'Canada', 'Spain', 'Germany',
    'Colombia', 'Argentina', 'Czech Republic', 'New Zealand', 'France',
    'Switzerland', 'Ukraine', 'Australia', 'Sweden', 'Romania', 'Hungary',
    'Denmark', 'Israel'
]

# === DATABASE SETUP ===
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
CSV_PATH = os.getenv('CSV_PATH')
engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# === DATA LOADERS ===
@st.cache_data
def load_csv_data():
    df = pd.read_csv(CSV_PATH)
    term_groups = pd.read_csv("term_groups.csv")
    merged = pd.merge(df, term_groups, how="left", on="translate")
    merged['final_term'] = merged['normalized_term'].fillna(merged['translate'])
    return merged

@st.cache_data
def get_postgres_data():
    query = """
    SELECT 
        c.country_name,
        c.country_code,
        r.region_name,
        r.region_name_final,
        t.term,
        t.translate,
        tr.week,
        tr.rank
    FROM trends tr
    JOIN countries c ON tr.country_code = c.country_code
    JOIN regions r ON tr.region_name = r.region_name AND tr.country_code = r.country_code
    JOIN terms t ON tr.term = t.term
    WHERE tr.rank BETWEEN 1 AND 5
    """
    return pd.read_sql(query, engine)


# === HELPER FUNCTIONS ===
def iso2_to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None

def normalize_str(s):
    if pd.isna(s): return ""
    s = str(s)
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'[^\w]', '', s)
    return s.lower()

@st.cache_data
def load_csv_with_final():
    df_clean = pd.read_csv(CSV_PATH, parse_dates=["week"])
    return df_clean[["country_name","region_name","region_name_final"]].drop_duplicates()

@st.cache_data
def load_geojson_for_country(iso3_code):
    folder = "Country Regions"
    pattern = f"gadm41_{iso3_code}_1.json"
    matches = glob.glob(os.path.join(folder, pattern))
    if not matches:
        st.warning(f"No GeoJSON file matching {pattern}")
        return None
    with open(matches[0], "r", encoding="utf-8") as f:
        return json.load(f)

# === SIDEBAR MENU ===
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select View:",
    ["🏠 Home", "🌐 Global-Level Stats", "📍 Region & Country Level Stats"]
)

# === HOME PAGE ===
if page == "🏠 Home":
    st.markdown("""
    <div class="home-container">
        <div class="home-title">🌍 Google Trends International Dashboard 🌍</div>
        <div class="home-subtitle">
            Created by <strong>Tejas Tadikonda, Ryan Rosario, Andy Rodriguez</strong>, and <strong>Gabriel Gonzalez</strong><br><br>
            Explore trending search terms across the globe.<br>
            Check out <strong>global</strong>, <strong>country</strong>, and <strong>region</strong> level statistics using the navigation bar.
        </div>
    </div>
    """, unsafe_allow_html=True)

# === GLOBAL-LEVEL PAGE ===
elif page == "🌐 Global-Level Stats":
    st.title("🌐 Global-Level Stats")
    df_global = load_csv_data()

    # Frequent Rank 1 Terms Bar Chart
    st.header("🏆 Most Frequent Rank 1 Terms by Country")
    rank1_df = df_global[df_global['rank'] == 1]
    term_counts = (
        rank1_df
        .groupby(['country_name', 'translate'])
        .size()
        .reset_index(name='count')
    )
    max_counts = term_counts.groupby('country_name')['count'].transform('max')
    common_terms = term_counts[term_counts['count'] == max_counts]
    grouped = (
        common_terms
        .groupby('country_name')['translate']
        .apply(lambda x: ', '.join(sorted(x)))
        .reset_index()
    )
    counts = common_terms.groupby('country_name')['count'].first().reset_index()
    final_df = grouped.merge(counts, on='country_name').rename(
        columns={'translate': 'top_terms', 'count': 'count'}
    )
    df_sorted = final_df.sort_values('count', ascending=False).reset_index(drop=True)

    chunk_size = 6
    num_chunks = math.ceil(len(df_sorted) / chunk_size)
    page_num = st.selectbox(
        "Select Page",
        range(1, num_chunks + 1),
        format_func=lambda x: f"Page {x}"
    )
    chunk = df_sorted.iloc[(page_num - 1) * chunk_size: page_num * chunk_size]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=chunk['count'],
            y=chunk['country_name'],
            orientation='h',
            text=chunk['top_terms'],
            hoverinfo='text+x+y',
            marker_color='teal'
        )
    )
    fig.update_layout(
        title=f"Most Frequent Rank 1 Terms - Page {page_num}",
        xaxis_title="Frequency",
        yaxis_title="Country",
        height=500
    )
    st.plotly_chart(fig)

    # Term Popularity Across Countries
    st.header("📊 Term Popularity Across Countries")
    available_terms = sorted(df_global['final_term'].dropna().unique())
    selected_term = st.selectbox(
        "Choose a term to see where it was popular:",
        available_terms
    )
    term_df = df_global[df_global['final_term'] == selected_term]
    term_country_counts = (
        term_df
        .groupby('country_name')
        .size()
        .reset_index(name='count')
    )
    if not term_country_counts.empty:
        fig2 = px.bar(
            term_country_counts.sort_values('count', ascending=True),
            x='count',
            y='country_name',
            orientation='h',
            title=f"📈 Countries where '{selected_term}' was a Top Search"
        )
        st.plotly_chart(fig2)
    else:
        st.warning("No data found for the selected term.")

# === REGION-&-COUNTRY-LEVEL PAGE ===
elif page == "📍 Region & Country Level Stats":


    df = get_postgres_data()
    countries = sorted(df['country_name'].unique())
    selected_country = st.sidebar.selectbox("Select a Country", countries)
    weeks = sorted(df['week'].unique())
    sel_weeks = st.sidebar.multiselect("Select Weeks:", weeks, default=weeks)
    translate_toggle = st.sidebar.checkbox("Show Translated Terms", value=True)
    term_col = 'translate' if translate_toggle else 'term'
    df_country = df[(df['country_name'] == selected_country) & (df['week'].isin(sel_weeks))]

    csv_map = load_csv_with_final().rename(columns={"region_name_final": "region_name_final_mapped"})
    df_country = df_country.merge(csv_map, on=["country_name", "region_name"], how="left")
    df_country["region_name_final"] = df_country["region_name_final_mapped"]


    iso3 = iso2_to_iso3(df_country['country_code'].iloc[0])
    geojson = load_geojson_for_country(iso3)
    if geojson is None:
        st.stop()

    for feat in geojson['features']:
        feat['id'] = feat['properties']['NAME_1']
    regions = [f['id'] for f in geojson['features']]
    region_lookup = {normalize_str(r): r for r in regions}

    st.title(f"📍 Region & Country Level Stats for {selected_country}")
    st.subheader("🗺️ Select a Region (or leave All) to Filter Results")

    # 3) region selector
    region_sel = st.selectbox("Pick a Region:", ["All Regions"] + regions)

    # === Normalize and Match Region for Data and Map Separately ===
    if region_sel == "All Regions":
        df_slice = df_country.copy()
        selected_geojson_region = None
    else:
        norm_region_sel = normalize_str(region_sel)
        df_country["region_name_norm"] = df_country["region_name_final"].apply(normalize_str)

        # Step 1: Try to match user input with GeoJSON name (for map highlight)
        norm_geojson_names = {normalize_str(r): r for r in regions}
        selected_geojson_region = norm_geojson_names.get(norm_region_sel, None)

        # Step 2: Try to match with data
        df_slice = df_country[df_country["region_name_norm"] == norm_region_sel]

        if df_slice.empty:
            # Try fuzzy match for data only
            choices = df_country["region_name_norm"].dropna().unique().tolist()
            matches = get_close_matches(norm_region_sel, choices, n=1, cutoff=0.8)
            if matches:
                fallback_norm = matches[0]
                fallback_row = df_country[df_country["region_name_norm"] == fallback_norm].iloc[0]
                fallback_display = fallback_row["region_name_final"]
                st.warning(f"⚠️ No exact data for '{region_sel}', using '{fallback_display}' for data...")

                df_slice = df_country[df_country["region_name_norm"] == fallback_norm]

                # Re-lookup correct GeoJSON name using original input region (not fallback)
                selected_geojson_region = norm_geojson_names.get(normalize_str(region_sel), None)
            else:
                st.warning(f"⚠️ No data for '{region_sel}', showing all regions...")
                df_slice = df_country.copy()
                selected_geojson_region = None
                region_sel = "All Regions"

    title_suffix = "" if region_sel == "All Regions" else f" – {region_sel}"


    # Map
    plot_df = pd.DataFrame({
        "region_name_final": regions,
        "value": [
            1 if (selected_geojson_region is None or r == selected_geojson_region) else 0.1
            for r in regions
        ]
    })

    fig = px.choropleth(
        plot_df,
        geojson=geojson,
        featureidkey="properties.NAME_1",
        locations="region_name_final",
        color="value",
        color_continuous_scale=["lightgrey", "steelblue"],
        title=f"{selected_country}{title_suffix}"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_traces(marker_line_width=0.5)
    st.plotly_chart(fig, use_container_width=True)


    # Metrics & Word Cloud
    left, right = st.columns([1,1])
    with left:
        st.subheader("📊 Key Metrics")
        m1, m2, m3 = st.columns(3)
        m1.metric("Unique Rank 1 Terms", df_slice[df_slice['rank'] == 1][term_col].nunique())
        m2.metric("Total Ranked Terms", df_slice[term_col].nunique())
        region_count = 1 if region_sel != "All Regions" else df_country["region_name_final"].nunique()
        m3.metric("Regions Selected", region_count)
        freq = df_slice[term_col].value_counts()
        if not freq.empty:
            top, cnt = freq.index[0], freq.iloc[0]
            st.subheader("🔁 Most Frequent Term")
            st.metric(label="Term", value=top, delta=f"Appeared {cnt} times")
    with right:
        st.subheader("☁️ Word Cloud")
        wc_col = term_col if selected_country in latin_script_countries else 'translate'
        text = " ".join(df_slice[wc_col].dropna().astype(str))
        if text:
            wc = WordCloud(width=400, height=200, background_color='white').generate(text)
            plt.figure(figsize=(6,3))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            st.pyplot(plt)
        else:
            st.write("No terms for word cloud.")

    # Latest Term Ranks
    st.subheader("📋 Latest Term Ranks")
    latest = (
        df_slice
        .sort_values(['rank','week'], ascending=[True,False])
        .drop_duplicates(term_col)[[term_col,'rank']]
    )
    html = "<div class='scroll-panel'><table><thead><tr><th>Term</th><th>Popularity</th></tr></thead><tbody>"
    for _, row in latest.iterrows():
        t, r = row[term_col], int(row['rank'])
        pct = int((6 - r) / 5 * 100)
        html += (
            f"<tr><td style='white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{t}</td>"
            f"<td><div style='background:#333;border-radius:4px;height:8px;overflow:hidden;'>"
            f"<div style='background:#1f77b4;width:{pct}%;height:100%;'></div></div></td></tr>"
        )
    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)
