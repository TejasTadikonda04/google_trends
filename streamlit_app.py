import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pycountry
import math

# === APP CONFIG ===
st.set_page_config(page_title="Interactive Trends Dashboard", layout="wide")

# === GLOBAL CSS ===
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background-color: #121212; color: #e0e0e0; }
  .scroll-panel { max-height: 350px; overflow-y: auto !important; padding: 8px; background-color: #1e1e1e; border-radius: 6px; }
  .scroll-panel table { width: 100%; border-collapse: collapse; }
  .scroll-panel th, .scroll-panel td { padding: 6px 8px; color: #e0e0e0; font-size: 14px; }
  .scroll-panel thead th { background-color: #2a2a2a; position: sticky; top: 0; z-index: 2; }
  .scroll-panel tbody tr:hover { background-color: #333; }
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

# === DATABASE SETUP FOR COUNTRY & REGION ===
try:
    import collections.abc as abc
    import collections
    collections.Hashable = abc.Hashable
    collections.Mapping = abc.Mapping
    collections.MutableMapping = abc.MutableMapping
except AttributeError:
    pass

db_user = 'postgres'
db_password = 'password'  # Update with actual password
db_host = 'localhost'
db_port = '5432'
db_name = 'trends_db'
engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

@st.cache_data
def get_postgres_data():
    query = """
    SELECT country_name, country_code, region_name, term, translate, week, rank
    FROM google_trends_international_cleaned
    WHERE rank BETWEEN 1 AND 5
    """
    return pd.read_sql(query, engine)

def iso2_to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None

# === CSV DATA LOADER FOR GLOBAL ===
@st.cache_data
def load_csv_data():
    trends_df = pd.read_csv("actualDataTeamProject.csv")
    term_groups = pd.read_csv("term_groups.csv")
    merged = pd.merge(trends_df, term_groups, how="left", on="translate")
    merged['final_term'] = merged['normalized_term'].fillna(merged['translate'])
    return merged

# === SIDEBAR MENU ===
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select View:", ["🌐 Global-Level Stats", "🌍 Country-Level Stats", "📍 Region-Level Stats"])

# === COUNTRY & REGION DATA ===
if page in ["🌍 Country-Level Stats", "📍 Region-Level Stats"]:
    df = get_postgres_data()
    countries = sorted(df['country_name'].unique())
    selected_country = st.sidebar.selectbox("Select a Country", countries)
    available_weeks = sorted(df['week'].unique())
    week_options = st.sidebar.multiselect("Select Weeks:", options=available_weeks, default=available_weeks)

    # Translation toggle
    translate_toggle = st.sidebar.checkbox("Show Translated Terms", value=True)
    term_col = 'translate' if translate_toggle else 'term'

    df_country = df[(df['country_name'] == selected_country) & (df['week'].isin(week_options))]

# === COUNTRY-LEVEL PAGE ===
if page == "🌍 Country-Level Stats":
    st.title("🌍 Interactive Global Search Trends")
    st.subheader(f"🗺️ Map View – {selected_country}")
    map_df = df_country.groupby(['country_name', 'country_code']).agg(best_rank=('rank', 'min')).reset_index()
    map_df['iso3'] = map_df['country_code'].apply(iso2_to_iso3)
    fig = px.choropleth(map_df, locations='iso3', locationmode='ISO-3', color='best_rank', color_continuous_scale='Blues', hover_name='country_name', projection='natural earth')
    fig.update_geos(fitbounds='locations', showcountries=True)
    st.plotly_chart(fig, use_container_width=True)
    
    left_col, right_col = st.columns([1, 1])
    with left_col:
        st.subheader("📊 Country Metrics")
        m1, m2, m3 = st.columns(3)
        m1.metric("Unique Rank 1 Terms", df_country[df_country['rank'] == 1][term_col].nunique())
        m2.metric("Total Ranked Terms", df_country[term_col].nunique())
        m3.metric("Regions", df_country['region_name'].nunique())
        freq_series = df_country[term_col].value_counts()
        if not freq_series.empty:
            top_term = freq_series.index[0]
            top_count = freq_series.iloc[0]
            st.subheader("🔁 Most Frequently Ranked Term")
            st.metric(label="Term", value=top_term, delta=f"Appeared {top_count} times")
    with right_col:
        st.subheader(f"☁️ Word Cloud: {selected_country}")

        # Latin-script logic
        if selected_country in latin_script_countries:
            wordcloud_col = term_col  # Respect the toggle
        else:
            wordcloud_col = 'translate'  # Force English for non-Latin

        text = " ".join(df_country[wordcloud_col].dropna().astype(str))
        if text:
            wordcloud = WordCloud(width=400, height=200, background_color='white').generate(text)
            plt.figure(figsize=(6, 3))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            st.pyplot(plt)
        else:
            st.write("No terms available for word cloud.")

    st.subheader("📋 Latest Term Ranks")
    latest = df_country.sort_values(['rank', 'week'], ascending=[True, False]).drop_duplicates(term_col)[[term_col, 'rank']]
    html = "<div class='scroll-panel'><table><thead><tr><th>Term</th><th>Popularity</th></tr></thead><tbody>"
    for _, row in latest.iterrows():
        term, rank = row[term_col], int(row['rank'])
        pct = int((6 - rank) / 5 * 100)
        html += f"<tr><td style='white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{term}</td><td><div style='background:#333;border-radius:4px;height:8px;overflow:hidden;'><div style='background:#1f77b4;width:{pct}%;height:100%;'></div></div></td></tr>"
    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)


# === REGION-LEVEL PAGE ===
elif page == "📍 Region-Level Stats":
    st.title(f"📍 Region-Level Stats for {selected_country}")
    st.subheader(f"🗺️ Map View – {selected_country}")
    map_df = df_country.groupby(['country_name', 'country_code']).agg(best_rank=('rank', 'min')).reset_index()
    map_df['iso3'] = map_df['country_code'].apply(iso2_to_iso3)
    fig = px.choropleth(map_df, locations='iso3', locationmode='ISO-3', color='best_rank', color_continuous_scale='Blues', hover_name='country_name', projection='natural earth')
    fig.update_geos(fitbounds='locations', showcountries=True)
    st.plotly_chart(fig, use_container_width=True)
    region = st.selectbox("Select a Region", sorted(df_country['region_name'].unique()), key="region_selector")
    r_df = df_country[df_country['region_name'] == region].sort_values("rank")
    st.subheader(f"Ranked Terms in {region}")
    html_r = "<div class='scroll-panel'><table><thead><tr><th>Term</th><th>Popularity</th></tr></thead><tbody>"
    for _, row in r_df.iterrows():
        term, rank = row[term_col], int(row['rank'])
        pct = int((6 - rank) / 5 * 100)
        html_r += f"<tr><td style='white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{term}</td><td><div style='background:#333;border-radius:4px;height:8px;overflow:hidden;'><div style='background:#1f77b4;width:{pct}%;height:100%;'></div></div></td></tr>"
    html_r += "</tbody></table></div>"
    st.markdown(html_r, unsafe_allow_html=True)

# === GLOBAL-LEVEL PAGE ===
elif page == "🌐 Global-Level Stats":
    st.title("🌐 Global-Level Stats")
    df_global = load_csv_data()

    # Frequent Rank 1 Terms Bar Chart
    st.header("🏆 Most Frequent Rank 1 Terms by Country")
    rank1_df = df_global[df_global['rank'] == 1]
    term_counts = rank1_df.groupby(['country_name', 'translate']).size().reset_index(name='count')
    max_counts = term_counts.groupby('country_name')['count'].transform('max')
    common_terms = term_counts[term_counts['count'] == max_counts].sort_values(['country_name', 'translate'])
    grouped = common_terms.groupby('country_name')['translate'].apply(lambda x: ', '.join(sorted(x))).reset_index()
    counts = common_terms.groupby('country_name')['count'].first().reset_index()
    final_df = grouped.merge(counts, on='country_name').rename(columns={'translate': 'top_terms', 'count': 'count'})
    df_sorted = final_df.sort_values('count', ascending=False).reset_index(drop=True)
    chunk_size = 6
    num_chunks = math.ceil(len(df_sorted) / chunk_size)
    page_num = st.selectbox("Select Page", range(1, num_chunks + 1), format_func=lambda x: f"Page {x}")
    chunk = df_sorted.iloc[(page_num - 1) * chunk_size: page_num * chunk_size]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=chunk['count'], y=chunk['country_name'], orientation='h', text=chunk['top_terms'], hoverinfo='text+x+y', marker_color='teal'))
    fig.update_layout(title=f"Most Frequent Rank 1 Terms - Page {page_num}", xaxis_title="Frequency", yaxis_title="Country", height=500)
    st.plotly_chart(fig)

    # Term Popularity Across Countries
    st.header("📊 Term Popularity Across Countries")
    available_terms = sorted(df_global['final_term'].dropna().unique())
    selected_term = st.selectbox("Choose a term to see where it was popular:", available_terms)
    term_df = df_global[df_global['final_term'] == selected_term]
    term_country_counts = term_df.groupby('country_name').size().reset_index(name='count')
    if not term_country_counts.empty:
        fig2 = px.bar(term_country_counts.sort_values('count', ascending=True), x='count', y='country_name', orientation='h', title=f"📈 Countries where '{selected_term}' was a Top Search")
        st.plotly_chart(fig2)
    else:
        st.warning("No data found for the selected term.")
