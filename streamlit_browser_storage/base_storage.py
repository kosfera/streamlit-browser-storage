from typing import Any, Union, Tuple
from uuid import uuid4
from datetime import date, datetime, timezone, timedelta
import json
import sys
import re

from streamlit_browser_storage.enums import Action


class BaseStorage:

    component = NotImplementedError

    max_entries_count = NotImplementedError

    max_entry_size = NotImplementedError  # bytes

    def set(
        self,
        name,
        value,
        ttl=None,
    ):
        expires_at = None
        if ttl:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)

        name, value, expires_at = self._validate(name, value, expires_at)

        self._send_to_component(
            Action.SET,
            name=name,
            value=value,
            expires_at=expires_at)

    def get(self, name: str) -> Any:
        self._delete_expired()

        return self._get_with_expiry(name)[0]

    def _get_with_expiry(self, name):

        value = self._send_to_component(Action.GET, name=name)
        return self._deserialize_value(value)

    def get_all(self):
        self._delete_expired()

        return {
            name: entry["value"]
            for name, entry in self._get_all_with_expiry().items()
        }

    def _get_all_with_expiry(self):
        entries = {}
        for name, value in self._send_to_component(Action.GET_ALL).items():
            value, expires_at = self._deserialize_value(value)

            entries[name] = {
                "value": value,
                "expires_at": expires_at,
            }

        return entries

    def expires_in(self, name: str) -> int:
        self._delete_expired()

        _, expires_at = self._get_with_expiry(name)
        if not expires_at:
            return

        now = int(datetime.now(timezone.utc).timestamp())
        expires_at = int(expires_at.timestamp())

        return expires_at - now

    def exists(self, name: str) -> bool:
        self._delete_expired()

        return self.get(name) is not None

    def delete(self, name: str) -> None:
        self._send_to_component(Action.DELETE, name=name)

    def _delete_expired(self) -> None:
        now = datetime.now(timezone.utc)
        for name, entry in self._get_all_with_expiry().items():
            expires_at = entry["expires_at"]

            if expires_at and expires_at <= now:
                self.delete(name)

    def _send_to_component(self, action, **kwargs):
        return self.component(action=action.value, key=str(uuid4()), **kwargs)

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

        split_index = isoformat.search(value).span()[0]
        value, expires_at = value[:split_index], value[split_index + 1:]

        if expires_at:
            expires_at = datetime.fromtimestamp(int(expires_at), timezone.utc)

        else:
            expires_at = None

        return json.loads(value), expires_at
