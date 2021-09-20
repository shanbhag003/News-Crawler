import pandas as pd
import streamlit as st
from requests_html import HTMLSession, HTML
from bs4 import BeautifulSoup
import requests
import urllib


# Sets the layout to full width
st.set_page_config(layout= "wide")

# Web App Title
st.title('''**News Crawler**''')

#Fixed format of crawling site link
url = 'https://news.google.com/rss/search?q='

# Sidebar - Specify Operation
input_operation = st.sidebar.selectbox(label="What would you like to do?", options=["Search News"])


if input_operation == "Search News":
    st.subheader("This app gives you news articles related to the person you want to see. Main functions of this app are:")
    st.write("1. Display all the news headlines around the world.")
    st.write("2. Display the Top 10 news articles.")
    st.write("2. Display links of news articles.")
    st.write("3. Give Sentiment score of the extracted news articles.")
    input_sub_operation = st.selectbox("Select any one of the activity", ["See the headlines", "Display Top 10 News headlines"])

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
            for news in soup.find_all('item'):
                head.append(news.title.text)
            headlines = pd.DataFrame(head, columns=['Headlines'])


            src = []
            for news in soup.find_all('item'):  # printing news
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
            for text in urls:
                t = text.replace('<link/>', "")
                urls1.append(t)

            links = pd.DataFrame(urls1, columns=['Links'])
            links = links.drop(0).reset_index()
            links = pd.DataFrame(links['Links'])

            def make_clickable(link):
                # target _blank to open new window
                # extract clickable text to display for your link
                #text = link.split('=')[1]
                return f'<a target="_blank" href="{link}">{link}</a>'


            # link is the column with hyperlinks
            links['Links'] = links['Links'].apply(make_clickable)


            OUTPUT = pd.concat([headlines, links, source], axis=1)  # Normal
            st.write(OUTPUT.to_html(escape=False, index=False), unsafe_allow_html=True)


        elif input_sub_operation == "Display Top 10 News headlines":
            st.success("Fetching Best news headlines")

            # Add as many, separated by '-'
            keyword = parameter_first_name + '-' + parameter_last_name + '-' + parameter_organization_name + '-' + parameter_country_name
            search = url + keyword

            # For Headline/Date/Source/Description
            reqs = requests.get(search)
            soup = BeautifulSoup(reqs.text, 'lxml')

            head = []
            for news in soup.find_all('item'):
                head.append(news.title.text)
            headlines = pd.DataFrame(head, columns=['Headlines'])
            top_head = headlines.head(10)


            src = []
            for news in soup.find_all('item'):  # printing news
                src.append(news.source.text)

            source = pd.DataFrame(src, columns=['Source/Publishers'])
            top_src = source.head(10)

            # For Links
            s = HTMLSession()
            response = s.get(search)

            urls = []
            for link in response.html.find('link'):
                urls.append(link.html)

            # Removing <link> tag from urls
            urls1 = []
            for text in urls:
                t = text.replace('<link/>', "")
                urls1.append(t)

            links = pd.DataFrame(urls1, columns=['Links'])
            links = links.drop(0).reset_index()
            links = pd.DataFrame(links['Links'])

            def make_clickable(link):
                # target _blank to open new window
                # extract clickable text to display for your link
                #text = link.split('=')[1]
                return f'<a target="_blank" href="{link}">{link}</a>'


            # link is the column with hyperlinks
            links['Links'] = links['Links'].apply(make_clickable)
            top_links = links.head(10)

            TOP_OUTPUT = pd.concat([top_head, top_links, top_src], axis=1)  # Normal
            st.write(TOP_OUTPUT.to_html(escape=False, index=False), unsafe_allow_html=True)













