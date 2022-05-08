from pathlib import Path

import streamlit.components.v1 as components


IS_RELEASE = False

if IS_RELEASE:
    component = components.declare_component(
        "browser_storage",
        path=Path(__file__).parent / "frontend/build")

else:
    component = components.declare_component(
        "browser_storage",
        url="http://localhost:3000")
