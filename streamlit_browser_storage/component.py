from pathlib import Path

import streamlit.components.v1 as components

frontend_build = Path(__file__).parent / "frontend/build"

if frontend_build.exists():
    component = components.declare_component("browser_storage", path=frontend_build)

else:
    component = components.declare_component("browser_storage", url="http://localhost:3000")
