import pandas as pd
from textblob import TextBlob
import streamlit as st
from requests_html import HTMLSession, HTML
from bs4 import BeautifulSoup
import requests
import re
from PIL import Image
from newspaper import Article

#Sets the layout to full width
st.set_page_config(layout= "wide")
image = Image.open("logo.png")
st.image(image)

# Web App Title
st.title('''**IntelliAdora's News Crawler**''')

#Fixed format of crawling site link
url = 'https://news.google.com/rss/search?q='

# Sidebar - Specify Operation
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
        if input_sub_operation == "See the headlines":
            st.success("Fetching Headlines")

            # Add as many, separated by '-'
            keyword = parameter_first_name + '-' + parameter_last_name + '-' + parameter_organization_name + '-' + parameter_country_name
            search = url + keyword

            # For Headline/Date/Source/Description
            reqs = requests.get(search)
            soup = BeautifulSoup(reqs.text, 'lxml')

            head = []
            for news in soup.find_all('item', limit = 50):
                head.append(news.title.text)
            headlines = pd.DataFrame(head, columns=['Headlines'])


            src = []
            for news in soup.find_all('item', limit = 50):  # printing news
                src.append(news.source.text)

            source = pd.DataFrame(src, columns=['Source/Publishers'])

            # For Links
            s = HTMLSession()
            response = s.get(search)

            urls = []
            for link in response.html.find('link'):
                urls.append(link.html)

            # Removing <link> tag from urls
            urls1 = []
            for text in urls[:51]:
                t = text.replace('<link/>', "")
                urls1.append(t)

            links = pd.DataFrame(urls1, columns=['Links'])
            links = links.drop(0).reset_index()
            links = pd.DataFrame(links['Links'])
            top_links = links.head(50)

            def make_clickable(link):
                # target _blank to open new window
                # extract clickable text to display for your link
                #text = link.split('=')[1]
                return f'<a target="_blank" href="{link}">{link}</a>'


            # link is the column with hyperlinks
            links['Links'] = links['Links'].apply(make_clickable)


            OUTPUT = pd.concat([headlines, links, source], axis=1)  # Normal
            st.info("Articles. as per ranking")
            st.write(OUTPUT.to_html(escape=False, index=False), unsafe_allow_html=True)


        elif input_sub_operation == "Display news summary":
            st.success("Fetching news summary")

            # Add as many, separated by '-'
            keyword = parameter_first_name + '-' + parameter_last_name + '-' + parameter_organization_name + '-' + parameter_country_name
            search = url + keyword

            # For Headline/Date/Source/Description
            reqs = requests.get(search)
            soup = BeautifulSoup(reqs.text, 'lxml')

            head = []
            for news in soup.find_all('item', limit = 50):
                head.append(news.title.text)
            headlines = pd.DataFrame(head, columns=['Headlines'])


            # For Links
            s = HTMLSession()
            response = s.get(search)

            urls = []
            for link in response.html.find('link'):
                urls.append(link.html)

            # Removing <link> tag from urls
            urls1 = []
            for text in urls[:51]:
                t = text.replace('<link/>', "")
                urls1.append(t)

            links = pd.DataFrame(urls1, columns=['Links'])
            links = links.drop(0).reset_index()
            links = pd.DataFrame(links['Links'])

            summ = []
            for i in urls1:
                try:
                    article = Article(i)
                    article.download()
                    article.parse()
                    summ.append(article.text)
                except:
                    summ.append("No Text")

            article = pd.DataFrame(summ, columns=['Article']).drop(0).reset_index()
            article = pd.DataFrame(article['Article'])

            SUMMARY_OUTPUT = pd.concat([headlines, article], axis=1)

            # function to clean the headlines
            def cleantext(text):
                text = re.sub('@[A-Za-z0–9]+', '', text)
                text = re.sub('#', '', text)
                text = re.sub('RT[\s]+', '', text)
                text = re.sub('https?:\/\/\S+', '', text)
                text = re.sub('\n', '', text)
                return text

            # Clean the headlines
            article = SUMMARY_OUTPUT['Article'].apply(cleantext)

            def make_clickable(link):
                # target _blank to open new window
                # extract clickable text to display for your link
                #text = link.split('=')[1]
                return f'<a target="_blank" href="{link}">{link}</a>'


            # link is the column with hyperlinks
            links['Links'] = links['Links'].apply(make_clickable)

            SUMMARY_OUTPUT = pd.concat([headlines, article, links], axis=1)  # Normal
            st.write(SUMMARY_OUTPUT.head(50).to_html(escape=False, index=False), unsafe_allow_html=True)

        else:
                st.success("Predicting Sentiment of articles")

                # Add as many, separated by '-'
                keyword = parameter_first_name + '-' + parameter_last_name + '-' + parameter_organization_name + '-' + parameter_country_name
                search = url + keyword

                # For Headline/Date/Source/Description
                reqs = requests.get(search)
                soup = BeautifulSoup(reqs.text, 'lxml')

                head = []
                for news in soup.find_all('item', limit = 50):
                    head.append(news.title.text)
                headlines = pd.DataFrame(head, columns=['Headlines'])

                # For Links
                s = HTMLSession()
                response = s.get(search)

                urls = []
                for link in response.html.find('link'):
                    urls.append(link.html)

                # Removing <link> tag from urls
                urls1 = []
                for text in urls[:51]:
                    t = text.replace('<link/>', "")
                    urls1.append(t)

                links = pd.DataFrame(urls1, columns=['Links'])
                links = links.drop(0).reset_index()
                links = pd.DataFrame(links['Links'])

                summ = []
                for i in urls1:
                    try:
                        article = Article(i)
                        article.download()
                        article.parse()
                        summ.append(article.text)
                    except:
                        summ.append("No Text")

                article = pd.DataFrame(summ, columns=['Article']).drop(0).reset_index()
                article = pd.DataFrame(article['Article'])


                def make_clickable(link):
                    # target _blank to open new window
                    # extract clickable text to display for your link
                    # text = link.split('=')[1]
                    return f'<a target="_blank" href="{link}">{link}</a>'


                # link is the column with hyperlinks
                links['Links'] = links['Links'].apply(make_clickable)

                SENTIMENT_OUTPUT = pd.concat([headlines, links, article], axis=1)  # Normal

                # function to clean the headlines
                def cleantext(text):
                    text = re.sub('@[A-Za-z0–9]+', '', text)
                    text = re.sub('#', '', text)
                    text = re.sub('RT[\s]+', '', text)
                    text = re.sub('https?:\/\/\S+', '', text)
                    return text

                # Clean the headlines
                article = SENTIMENT_OUTPUT['Article'].apply(cleantext)

                # Now we create a function which will check the polarity of headlines
                def getpolarity(text):
                    return TextBlob(text).sentiment.polarity

                # Create columns to store these values
                SENTIMENT_OUTPUT['Sentiment'] = SENTIMENT_OUTPUT['Article'].apply(getpolarity)

                # Create a function to analyse positive, neutral and negative headlines
                def getanalysis(score):
                    if score < 0:
                        return 'Negative'
                    elif score == 0:
                        return 'Neutral'
                    else:
                        return 'Positive'

                SENTIMENT_OUTPUT['Analysis'] = SENTIMENT_OUTPUT['Sentiment'].apply(getanalysis)

                SENTIMENT_OUTPUT = SENTIMENT_OUTPUT.drop(["Article","Sentiment"], axis =1)
                st.write(SENTIMENT_OUTPUT.head(50).to_html(escape=False, index=False), unsafe_allow_html=True)













