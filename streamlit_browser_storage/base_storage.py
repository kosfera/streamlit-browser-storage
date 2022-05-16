import json
import re
import sys
from datetime import datetime, timedelta, timezone
from enum import Enum, unique
from typing import Any, Tuple, Union

import streamlit as st

from streamlit_browser_storage.component import component


@unique
class Action(Enum):

    SET = "SET"

    GET = "GET"

    GET_ALL = "GET_ALL"

    DELETE = "DELETE"


@unique
class Source(Enum):

    SET = "SET"

    GET = "GET"

    GET_ALL = "GET_ALL"

    DELETE = "DELETE"

    EXPIRES_IN = "EXPIRES_IN"

    EXISTS = "EXISTS"


class BaseStorage:

    component = component

    max_entries_count = NotImplementedError

    max_entry_size = NotImplementedError  # bytes

    _keys = {}

    def __init__(self, key):
        self.key = key
        self.source = None
        self._keys = {}

    def set(
        self,
        name,
        value,
        ttl=None,
    ):
        self.source = Action.SET

        expires_at = None
        if ttl:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)

        name, value, expires_at = self._validate(name, value, expires_at)

        self._send_to_component(Action.SET, name=name, value=value, expires_at=expires_at)

    def get(self, name: str) -> Any:
        self.source = Source.GET

        return self._get_with_expiry(name)[0]

    def expires_in(self, name: str) -> int:
        self.source = Source.EXPIRES_IN

        _, expires_at = self._get_with_expiry(name)
        if not expires_at:
            return

        now = int(datetime.now(timezone.utc).timestamp())
        expires_at = int(expires_at.timestamp())

        return expires_at - now

    def exists(self, name: str) -> bool:
        self.source = Source.EXISTS

        return self.get(name) is not None

    def _get_with_expiry(self, name):

        value = self._send_to_component(Action.GET, name=name)
        return self._deserialize_value(value)

    def get_all(self):
        self.source = Source.GET_ALL

        return {name: entry["value"] for name, entry in self._get_all_with_expiry().items()}

    def _get_all_with_expiry(self):
        entries = {}
        for name, value in (self._send_to_component(Action.GET_ALL) or {}).items():
            value, expires_at = self._deserialize_value(value)

            entries[name] = {
                "value": value,
                "expires_at": expires_at,
            }

        return entries

    def delete(self, name: str) -> None:
        self.source = Source.DELETE

        self._send_to_component(Action.DELETE, name=name)

    def _send_to_component(self, action, **kwargs):

        key_prefix = (
            f"/storages/{self.__class__.__name__}"
            f"/keys/{self.key}"
            f"/sources/{self.source.value}"
            f"/actions/{action.value}"
        )
        self._keys.setdefault(key_prefix, 0)
        self._keys[key_prefix] += 1

        key = f"{key_prefix}_{self._keys[key_prefix]}"

        value = self.component(type=self.__class__.__name__, action=action.value, key=key, **kwargs)

        try:
            del st.session_state[key]
        except KeyError:
            pass

        if value:
            return json.loads(value)

    def _validate(self, name: str, value: Any, expires_at: datetime = None) -> None:
        # NAME validation
        if not name:
            raise ValueError("One must provide non-empty `name`")

        if not isinstance(name, str):
            raise ValueError("`name` must be a string")

        # VALUE validation
        if not value:
            raise ValueError(
                "One must provide non-empty `value` otherwise just delete that specific entry"
            )

        try:
            value = self._serialize_value(value, expires_at)

        except TypeError:
            raise ValueError("One must provide JSON-serializable `value`")

        # NAMES count
        existing_names = self._get_all_with_expiry().keys()
        if (
            name not in existing_names
            and self.max_entries_count
            and len(existing_names) >= self.max_entries_count
        ):
            raise ValueError(
                f"Allowed maximum number of {self.max_entries_count} `names` has beed exceeded. "
                "Remove some before adding more"
            )

        # NAME + VALUE
        if self.max_entry_size and sys.getsizeof(name + value) > self.max_entry_size:
            raise ValueError(
                "`name` and `value` combined bytes size exceeded allowed maximum "
                f"{self.max_entry_size} bytes"
            )

        if expires_at:
            expires_at = expires_at.isoformat()

        return name, value, expires_at

    def _serialize_value(self, value: Any, expires_at: datetime = None):
        if expires_at:
            return f"{json.dumps(value)}|{int(expires_at.timestamp())}"

        else:
            return f"{json.dumps(value)}|"

    def _deserialize_value(self, value: str) -> Tuple[Any, Union[datetime, None]]:
        isoformat = re.compile(r"\|(\d+|)$")

        m = None
        if value:
            m = isoformat.search(value)

        expires_at = None
        if m:
            split_index = m.span()[0]
            value, expires_at = value[:split_index], value[split_index + 1 :]

        if expires_at:
            expires_at = datetime.fromtimestamp(int(expires_at), timezone.utc)

        else:
            expires_at = None

        try:
            return json.loads(value), expires_at

        except (TypeError, json.JSONDecodeError):
            return value, expires_at
