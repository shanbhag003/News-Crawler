import pandas as pd
from textblob import TextBlob
import streamlit as st
from bs4 import BeautifulSoup
import requests
import re
from PIL import Image
from readability import Document  # ✅ Replacing newspaper3k

# Set layout to wide
st.set_page_config(layout="wide")
image = Image.open("logo.png")
st.image(image)

# Title
st.title("**IntelliAdora's News Crawler**")

# Base RSS URL
url = 'https://news.google.com/rss/search?q='

# Sidebar operation
input_operation = st.sidebar.selectbox(label="What would you like to do?", options=["Search News"])

if input_operation == "Search News":
    st.subheader("This app gives you news articles related to the person you want to see. Main functions of this app are:")
    st.write("1. Displays all the news headlines around the world with link and source.")
    st.write("2. Displays summary of extracted news articles.")
    st.write("3. Predicts Sentiment of the extracted news article.")

    input_sub_operation = st.selectbox("Select any one of the activity", ["See the headlines", "Display news summary", "Predict Sentiment"])

    parameter_first_name = st.text_input("Enter First Name of the person you want to search")
    parameter_last_name = st.text_input("Enter Last Name of the person you want to search")
    parameter_organization_name = st.text_input("Enter the name of Organization where the person works.")
    parameter_country_name = st.text_input("Enter Country where the person lives.")

    if st.button("Fetch"):
        keyword = parameter_first_name + '-' + parameter_last_name + '-' + parameter_organization_name + '-' + parameter_country_name
        search = url + keyword

        reqs = requests.get(search)
        soup = BeautifulSoup(reqs.text, 'lxml')

        headlines_list = [news.title.text for news in soup.find_all('item', limit=50)]
        sources_list = [news.source.text if news.source else "Unknown" for news in soup.find_all('item', limit=50)]
        urls_list = [link.text for link in soup.find_all('link')][1:51]

        def make_clickable(link):
            return f'<a target="_blank" href="{link}">{link}</a>'

        links_df = pd.DataFrame(urls_list, columns=['Links'])
        links_df['Links'] = links_df['Links'].apply(make_clickable)
        headlines_df = pd.DataFrame(headlines_list, columns=['Headlines'])
        sources_df = pd.DataFrame(sources_list, columns=['Source/Publishers'])

        if input_sub_operation == "See the headlines":
            st.success("Fetching Headlines")
            output = pd.concat([headlines_df, links_df, sources_df], axis=1)
            st.info("Articles as per ranking")
            st.write(output.to_html(escape=False, index=False), unsafe_allow_html=True)

        elif input_sub_operation == "Display news summary":
            st.success("Fetching news summary")

            summaries = []
            for link in urls_list:
                try:
                    article_html = requests.get(link, timeout=10).text
                    doc = Document(article_html)
                    text = BeautifulSoup(doc.summary(), 'lxml').get_text()
                    summaries.append(text)
                except:
                    summaries.append("No Text")

            def cleantext(text):
                text = re.sub('@[A-Za-z0–9]+', '', text)
                text = re.sub('#', '', text)
                text = re.sub('RT[\s]+', '', text)
                text = re.sub('https?:\/\/\S+', '', text)
                text = re.sub('\n', '', text)
                return text

            summaries_clean = pd.Series(summaries).apply(cleantext)
            summary_output = pd.concat([headlines_df, summaries_clean.rename("Article"), links_df], axis=1)
            st.write(summary_output.to_html(escape=False, index=False), unsafe_allow_html=True)

        else:
            st.success("Predicting Sentiment of articles")

            summaries = []
            for link in urls_list:
                try:
                    article_html = requests.get(link, timeout=10).text
                    doc = Document(article_html)
                    text = BeautifulSoup(doc.summary(), 'lxml').get_text()
                    summaries.append(text)
                except:
                    summaries.append("No Text")

            def cleantext(text):
                text = re.sub('@[A-Za-z0–9]+', '', text)
                text = re.sub('#', '', text)
                text = re.sub('RT[\s]+', '', text)
                text = re.sub('https?:\/\/\S+', '', text)
                return text

            def getpolarity(text):
                return TextBlob(text).sentiment.polarity

            def getanalysis(score):
                if score < 0:
                    return 'Negative'
                elif score == 0:
                    return 'Neutral'
                else:
                    return 'Positive'

            cleaned_articles = pd.Series(summaries).apply(cleantext)
            sentiment_scores = cleaned_articles.apply(getpolarity)
            sentiment_labels = sentiment_scores.apply(getanalysis)

            sentiment_output = pd.concat([headlines_df, links_df, sentiment_labels.rename("Sentiment")], axis=1)
            st.write(sentiment_output.to_html(escape=False, index=False), unsafe_allow_html=True)
