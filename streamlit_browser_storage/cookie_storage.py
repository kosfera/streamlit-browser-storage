from streamlit_browser_storage.base_storage import BaseStorage


# Web Browser   | Maximum cookies | Maximum size per cookie
# --------------+-----------------+------------------------
# Google Chrome | 180             | 4096 bytes
# Firefox       | 150             | 4097 bytes
# Opera         | 180             | 4096 bytes
# Android       | 50              | 4096 bytes
class CookieStorage(BaseStorage):

    max_entries_count = 50

    max_entry_size = 4096  # bytes
