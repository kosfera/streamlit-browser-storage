# import os

# import streamlit.components.v1 as components
# from cookies_jar import CookiesJar as BaseCookiesJar


# IS_RELEASE = False

# if IS_RELEASE:
#     absolute_path = os.path.dirname(os.path.abspath(__file__))
#     build_path = os.path.join(absolute_path, "frontend/build")
#     _cookies_jar = components.declare_component("cookies_jar", path=build_path)

# else:
#     _cookies_jar = components.declare_component("cookies_jar", url="http://localhost:3001")


# class CookiesJar(BaseCookiesJar):

#     jar = _cookies_jar
