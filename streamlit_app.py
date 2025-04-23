# Word cloud
import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import math
import plotly.graph_objects as go


# Load data
@st.cache_data
def load_data():
    return pd.read_csv("actualDataTeamProject.csv")

df = load_data()

# Streamlit app
st.title("Google Trends Word Cloud by Country")

# Dropdown to select a country
country = st.selectbox("Choose a country:", sorted(df['country_name'].dropna().unique()))

# Filter dataset
filtered_df = df[df['country_name'] == country]

# Join all search terms (translated) into a single string
text = " ".join(filtered_df['translate'].dropna().astype(str))

# Generate word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

# Display the word cloud
st.subheader(f"Top Rising Search Terms in {country}")
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
st.pyplot(plt)


# Creates a dataframe only conisisting of rows with rank 1
rank1_df = df[df['rank'] == 1]

# Creates a new dataframe that consist of each country's rank 1 terms and how often they 
term_counts = rank1_df.groupby(['country_name', 'translate']).size().reset_index(name='count')
max_counts = term_counts.groupby('country_name')['count'].transform('max')
common_terms = term_counts[term_counts['count'] == max_counts].copy()
common_terms['term_rank_by_freq'] = 1
common_terms = common_terms.sort_values(['country_name', 'translate'])

# Functions that joins terms together for a specific country
def join_sorted(series):
    return ', '.join(sorted(series))

# Creates a new DataFrame that consist of each combines each country's most frequent rank 1 terms 
grouped = (
    common_terms
    .groupby('country_name')['translate']
    .apply(join_sorted)
    .reset_index()
)
counts = common_terms.groupby('country_name')['count'].first().reset_index()
final_df = grouped.merge(counts, on='country_name')
final_df.columns = ['country_name', 'top_terms', 'count']


# Sorts dataframe based on number of occurences
df_sorted = final_df.sort_values('count', ascending=False).reset_index(drop=True)

# Displays the bar chart
st.title("Most Frequent Rank 1 Search Terms by Country")
chunk_size = 6
num_chunks = math.ceil(len(df_sorted) / chunk_size)
page = st.selectbox("Select Page", range(1, num_chunks + 1), format_func=lambda x: f"Page {x}")
chunk = df_sorted.iloc[(page - 1) * chunk_size: page * chunk_size]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=chunk['count'],
    y=chunk['country_name'],
    orientation='h',
    text=chunk['top_terms'],
    hoverinfo='text+x+y',
    marker_color='teal'
))

fig.update_layout(
    title=f"Most Frequent Rank 1 Terms - Page {page}",
    xaxis_title="Frequency",
    yaxis_title="Country",
    height=500
)

# Display chart
st.plotly_chart(fig)
