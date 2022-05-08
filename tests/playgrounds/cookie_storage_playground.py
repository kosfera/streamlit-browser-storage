import streamlit as st
from streamlit_browser_storage import CookieStorage


s = CookieStorage(key="test")

st.json(s.get_all())
s.set("some_cookie", "test")
# s.set("maciej", "test2")
# s.set("maciej", "test3", ttl=4)
# st.write(s.expires_in("maciej"))
