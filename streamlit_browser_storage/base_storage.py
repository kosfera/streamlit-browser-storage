from ast import excepthandler
from typing import Any, Union, Tuple
from datetime import datetime, timezone, timedelta
import json
import sys
import re
from enum import Enum, unique

import streamlit as st


@unique
class Action(Enum):

    SET = "SET"

    GET = "GET"

    GET_ALL = "GET_ALL"

    DELETE = "DELETE"


class BaseStorage:

    component = NotImplementedError

    max_entries_count = NotImplementedError

    max_entry_size = NotImplementedError  # bytes

    def __init__(self, key):
        self.key = key
        self.key_prefixes = {
            "set": 0,
            "get": 0,
            "get_all": 0,
            "delete": 0,
            "expires_in": 0,
            "exists": 0,
        }

    def set(
        self,
        name,
        value,
        ttl=None,
    ):
        self.key_prefixes["set"] += 1
        self.key_prefix = f"set{self.key_prefixes['set']}"

        expires_at = None
        if ttl:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)

        name, value, expires_at = self._validate(name, value, expires_at)

        self._send_to_component(
            Action.SET,
            key="set",
            name=name,
            value=value,
            expires_at=expires_at)

    def get(self, name: str) -> Any:
        self.key_prefixes["get"] += 1
        self.key_prefix = f"get{self.key_prefixes['get']}"

        self._delete_expired()

        return self._get_with_expiry(name)[0]

    def _get_with_expiry(self, name):

        value = self._send_to_component(Action.GET, key="_get_with_expiry", name=name)
        return self._deserialize_value(value)

    def get_all(self):
        self.key_prefixes["get_all"] += 1
        self.key_prefix = f"get_all{self.key_prefixes['get_all']}"

        self._delete_expired()

        return {
            name: entry["value"]
            for name, entry in self._get_all_with_expiry(key="get_all").items()
        }

    def _get_all_with_expiry(self, key=None):
        entries = {}
        for name, value in (self._send_to_component(Action.GET_ALL, key=key or "_get_all_with_expiry") or {}).items():
            value, expires_at = self._deserialize_value(value)

            entries[name] = {
                "value": value,
                "expires_at": expires_at,
            }

        return entries

    def expires_in(self, name: str) -> int:
        self.key_prefixes["expires_in"] += 1
        self.key_prefix = f"expires_in{self.key_prefixes['expires_in']}"

        self._delete_expired()

        _, expires_at = self._get_with_expiry(name)
        if not expires_at:
            return

        now = int(datetime.now(timezone.utc).timestamp())
        expires_at = int(expires_at.timestamp())

        return expires_at - now

    def exists(self, name: str) -> bool:
        self.key_prefixes["exists"] += 1
        self.key_prefix = f"exists{self.key_prefixes['exists']}"

        self._delete_expired()

        return self.get(name) is not None

    def delete(self, name: str) -> None:
        self.key_prefixes["delete"] += 1
        self.key_prefix = f"delete{self.key_prefixes['delete']}"

        self._send_to_component(Action.DELETE, key="delete", name=name)

    def _delete_expired(self) -> None:
        now = datetime.now(timezone.utc)
        for name, entry in self._get_all_with_expiry().items():
            expires_at = entry["expires_at"]

            if expires_at and expires_at <= now:
                self.delete(name)

    def _send_to_component(self, action, key, **kwargs):

        key = f"browser_storage__{self.key_prefix}_{key}"

        value = self.component(
            type=self.__class__.__name__,
            action=action.value,
            key=key,
            **kwargs)

        del st.session_state[key]
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
                "One must provide non-empty `value` otherwise just delete that specific entry")

        try:
            value = self._serialize_value(value, expires_at)

        except TypeError:
            raise ValueError("One must provide JSON-serializable `value`")

        # NAMES count
        existing_names = self._get_all_with_expiry().keys()
        if name not in existing_names and len(existing_names) >= self.max_entries_count:
            raise ValueError(
                f"Allowed maximum number of {self.max_entries_count} `names` has beed exceeded. "
                "Remove some before adding more")

        # NAME + VALUE
        if sys.getsizeof(name + value) > self.max_entry_size:
            raise ValueError(
                "`name` and `value` combined bytes size exceeded allowed maximum "
                f"{self.max_entry_size} bytes")

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
            value, expires_at = value[:split_index], value[split_index + 1:]

        if expires_at:
            expires_at = datetime.fromtimestamp(int(expires_at), timezone.utc)

        else:
            expires_at = None

        try:
            return json.loads(value), expires_at

        except json.JSONDecodeError:
            return value, expires_at
