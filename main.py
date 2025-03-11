import os
import sqlite3
import streamlit as st
from rag import process_urls, generate_answer

# Download and build SQLite 3.49+ inside Streamlit Cloud
os.system("wget https://www.sqlite.org/2025/sqlite-autoconf-3490100.tar.gz")
os.system("tar xvfz sqlite-autoconf-3490100.tar.gz")
os.system("cd sqlite-autoconf-3490100 && ./configure --prefix=/home/appuser/.local && make && make install")

# Force Python to use the compiled SQLite version
os.environ["LD_LIBRARY_PATH"] = "/home/appuser/.local/lib"
os.environ["PATH"] = "/home/appuser/.local/bin:" + os.environ["PATH"]


st.title("News Research Tool")

url1 = st.sidebar.text_input("URL 1")
url2 = st.sidebar.text_input("URL 2")
url3 = st.sidebar.text_input("URL 3")

placeholder = st.empty()

process_url_button = st.sidebar.button("Process URLs")
if process_url_button:
    urls = [url for url in (url1, url2, url3) if url!='']
    if len(urls) == 0:
        placeholder.text("You must provide at least one valid url")
    else:
        for status in process_urls(urls):
            placeholder.text(status)


query = placeholder.text_input("Question")
if query:
    try:
        answer, sources = generate_answer(query)
        st.header("Answer:")
        st.write(answer)

        if sources:
            st.subheader("Sources:")
            for source in sources.split("\n"):
                st.write(source)
    except RuntimeError as e:
        placeholder.text("You must process urls first")

