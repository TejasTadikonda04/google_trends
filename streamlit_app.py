# Word cloud
import streamlit_app as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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
