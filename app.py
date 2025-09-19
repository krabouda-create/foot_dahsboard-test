import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Foot", layout="wide")

st.title("⚽ Dashboard Football - Version Polish")

uploaded_file = st.file_uploader("Importer un fichier CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)

    if "score" in df.columns:
        st.subheader("Histogramme des scores")
        fig, ax = plt.subplots()
        df['score'].plot(kind='hist', ax=ax)
        st.pyplot(fig)
