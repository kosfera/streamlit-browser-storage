from streamlit_browser_storage.base_storage import BaseStorage


class LocalStorage(BaseStorage):

    max_entries_count = None

    max_entry_size = None  # bytes
