# Rwanda Distance-Based Fare Sentiment Dashboard
# Built using Streamlit (streamlit.io)

import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob
import re

# -------------------- Sample Data Generation --------------------
@st.cache_data
def generate_sample_data():
    data = {
        'date': pd.date_range(start='2025-04-01', periods=30, freq='D'),
        'comment': [
            "This new fare system is fairer, I support it.",
            "Too expensive for long-distance travelers!",
            "I am confused about how the new fare works.",
            "It is a good initiative, but needs more clarity.",
            "Great move by the government.",
            "Unfair to students and low-income earners.",
            "People should stop spreading lies about the prices.",
            "It is confusing and no one explained it to us.",
            "Prices increased suddenly. Why?",
            "Much better than flat fares."
        ] * 3
    }
    df = pd.DataFrame(data)
    df['comment'] = df['comment'].sample(frac=1).values  # Shuffle comments
    return df

# -------------------- Sentiment Analysis --------------------
def get_sentiment(text):
    try:
        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0.1:
            return 'Positive'
        elif analysis.sentiment.polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    except Exception:
        return 'Neutral'

# -------------------- Word Cloud --------------------
def plot_wordcloud(data, sentiment_filter):
    text = " ".join(comment for comment in data[data['sentiment'] == sentiment_filter]['comment'])
    if not text:
        st.write("No data available for this sentiment.")
        return
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Rwanda Fare Sentiment Dashboard", layout="wide")
st.title("Rwanda Distance-Based Fare Public Sentiment Dashboard")

# Load Data
df = generate_sample_data()
df['sentiment'] = df['comment'].apply(get_sentiment)

# Tabs
tabs = st.tabs(["Overview", "Trends", "WordCloud", "Recommendations"])

# Overview
tabs[0].subheader("Overall Sentiment Distribution")
sentiment_counts = df['sentiment'].value_counts().reset_index()
sentiment_counts.columns = ['Sentiment', 'Count']
tabs[0].plotly_chart(px.pie(sentiment_counts, names='Sentiment', values='Count', title='Sentiment Pie Chart'))

# Trends
tabs[1].subheader("Sentiment Over Time")
daily_sentiment = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
daily_sentiment = daily_sentiment.reset_index()
tabs[1].plotly_chart(px.line(daily_sentiment, x='date', y=daily_sentiment.columns[1:], title='Sentiment Timeline'))

# WordCloud
sentiment_filter = tabs[2].selectbox("Select sentiment to visualize:", ["Positive", "Neutral", "Negative"])
tabs[2].subheader(f"WordCloud for {sentiment_filter} Comments")
plot_wordcloud(df, sentiment_filter)

# Recommendations
tabs[3].subheader("Insights and Recommendations")
if sentiment_counts.loc[sentiment_counts['Sentiment'] == 'Negative', 'Count'].values[0] > 10:
    tabs[3].warning("High negative sentiment detected. Consider public awareness campaigns and fare calculators to educate citizens.")
else:
    tabs[3].success("Public perception is mostly positive or neutral.")

if 'confusing' in df['comment'].str.lower().str.cat(sep=' '):
    tabs[3].info("Multiple users mentioned confusion - consider improving communication about how fares are calculated.")

st.markdown("---")
st.caption("Developed for the Tech Associates Hackathon 2025")
