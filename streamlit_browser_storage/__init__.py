from pathlib import Path

import streamlit.components.v1 as components

from cookie_storage import CookieStorage
from local_storage import LocalStorage
from session_storage import SessionStorage


IS_RELEASE = False

if IS_RELEASE:
    _browser_storage = components.declare_component(
        "browser_storage",
        path=Path(__file__).parent / "frontend/build")

else:
    _browser_storage = components.declare_component(
        "browser_storage",
        url="http://localhost:3000")


CookieStorage.component = _browser_storage
LocalStorage.component = _browser_storage
SessionStorage.component = _browser_storage

import streamlit as st

s = CookieStorage(key="test")

st.json(s.get_all())
s.set("maciej", "test")
s.set("maciej", "test2")
s.set("maciej", "test3", ttl=10)
st.write(s.get_all())
st.write(s.expires_in("maciej"))
