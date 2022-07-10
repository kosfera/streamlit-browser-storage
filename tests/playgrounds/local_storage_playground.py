import streamlit as st

from streamlit_browser_storage import LocalStorage

with st.echo():
    s = LocalStorage(key="test")

    k = "some_key"
    if not s.exists(k):
        s.set(k, "1")

    if st.button("Increment"):
        v = int(s.get(k) or "0")

        s.set(k, v + 1)

    v = int(s.get(k) or "0")
    st.write("VALUE", v)

    st.write(s.get(k))
