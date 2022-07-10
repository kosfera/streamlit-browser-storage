
# Streamlit Browser Storage Component
## WARNING! This is still heavily work in progress. Use at your own risk.

![build status](https://github.com/kosfera/streamlit-browser-storage/actions/workflows/lint_and_tests.yml/badge.svg)

Streamlit component allowing one to connect to the following browser storages:
- `cookies`
- `local storage`
- `session storage`

## Usage - cookies

```python
from streamlit_browser_storage import CookieStorage

s = CookieStorage(key="some_component_key")

s.set("some_key", "test")

print(s.get("some_key"))
print(s.get_all())
print(s.expires_in("some_key"))
print(s.exists("some_key"))
print(s.delete("some_key"))
```

## Usage - local storage

```python
from streamlit_browser_storage import LocalStorage

s = LocalStorage(key="some_component_key")

s.set("some_key", "test")

print(s.get("some_key"))
print(s.get_all())
print(s.expires_in("some_key"))
print(s.exists("some_key"))
print(s.delete("some_key"))
```

## Usage - session storage

```python
from streamlit_browser_storage import SessionStorage

s = SessionStorage(key="some_component_key")

s.set("some_key", "test")

print(s.get("some_key"))
print(s.get_all())
print(s.expires_in("some_key"))
print(s.exists("some_key"))
print(s.delete("some_key"))
```
