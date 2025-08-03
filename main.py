import streamlit as st
import pandas as pd

st.title("Life is Amazing")
data = pd.DataFrame({"animal": ["cat", "dog"], "cute": [10, 8]})
st.dataframe(data)

secret = st.text_input("Type here:")
if secret == "abracadabra":
    st.write("🎉 You unlocked the magic!")
