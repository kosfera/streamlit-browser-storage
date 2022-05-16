from datetime import date, datetime, timedelta, timezone
from unittest import TestCase

import pytest
from freezegun import freeze_time

from streamlit_browser_storage.base_storage import Action, BaseStorage


class ComponentMock:
    def __init__(self):
        self.storage = {}

    def __call__(self, action, name=None, value=None, expires_at=None, type=None, key=None):
        if action == Action.SET.value:
            self.storage[name] = value
            return True

        elif action == Action.GET.value:
            return self.storage.get(name) or "null|"

        elif action == Action.GET_ALL.value:
            return self.storage

        elif action == Action.DELETE.value:
            try:
                del self.storage[name]

            except KeyError:
                return True

            else:
                return False

    def clear(self):
        self.storage = {}


class BaseStorageWithMock(BaseStorage):

    component = ComponentMock()

    max_entries_count = 10

    max_entry_size = 1000


class BaseStorageTestCase(TestCase):
    def setUp(self):
        self.storage = BaseStorageWithMock(key="test")
        self.storage.component.clear()

        self.now = datetime.now(timezone.utc)
        self.seconds = lambda s: timedelta(seconds=s)

    #
    # SET
    #
    def test_set__simple_value__is_set(self):

        # GIVEN base storage
        # WHEN calling `set`
        self.storage.set("greeting", "hello")

        # THEN correct values is set
        assert self.storage.component.storage == {"greeting": '"hello"|'}

    def test_set__complex_value__is_set(self):

        # GIVEN base storage
        # WHEN calling `set`
        self.storage.set("greeting", ["hello", 1])

        # THEN correct values is set
        assert self.storage.component.storage == {"greeting": '["hello", 1]|'}

    def test_set__empty_name__is_not_set(self):

        # GIVEN base storage
        # WHEN calling `set`
        # THEN exceptions is raised
        with pytest.raises(ValueError) as e:
            self.storage.set("", ["hello", 1])

        assert e.value.args == ("One must provide non-empty `name`",)

    def test_set__name_not_string__is_not_set(self):

        # GIVEN base storage
        # WHEN calling `set`
        # THEN exceptions is raised
        with pytest.raises(ValueError) as e:
            self.storage.set(True, ["hello", 1])

        assert e.value.args == ("`name` must be a string",)

    def test_set__value_is_empty__is_not_set(self):

        # GIVEN base storage
        # WHEN calling `set`
        # THEN exceptions is raised
        with pytest.raises(ValueError) as e:
            self.storage.set("greetings", None)

        assert e.value.args == (
            "One must provide non-empty `value` otherwise just delete that specific entry",
        )

    def test_set__value_is_not_serializable__is_not_set(self):

        # GIVEN base storage
        # WHEN calling `set`
        # THEN exceptions is raised
        with pytest.raises(ValueError) as e:
            self.storage.set("greetings", date(2022, 1, 4))

        assert e.value.args == ("One must provide JSON-serializable `value`",)

    def test_set__storage_clogged_up__is_not_set(self):

        # GIVEN already clogged up storage
        for i in range(self.storage.max_entries_count):
            self.storage.set(f"name_{i}", f"value_{i}")

        # WHEN calling `set`
        # THEN exceptions is raised
        with pytest.raises(ValueError) as e:
            self.storage.set("greetings", "what?")

        assert e.value.args == (
            "Allowed maximum number of 10 `names` has beed exceeded. "
            "Remove some before adding more",
        )

    def test_set__name_value_size_too_large__is_not_set(self):

        # GIVEN base storage
        # WHEN calling `set`
        # THEN exceptions is raised
        with pytest.raises(ValueError) as e:
            self.storage.set("greetings", (self.storage.max_entry_size - 8) * "a")

        assert e.value.args == (
            "`name` and `value` combined bytes size exceeded allowed maximum 1000 bytes",
        )

    #
    # GET
    #
    def test_get__exists_simple_value__is_fetched(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", "hello")
        self.storage.set("hey", "ho")

        # WHEN calling `get`
        value = self.storage.get("greeting")

        # THEN correct values is returned
        assert value == "hello"

    def test_get__exists_complex_value__is_fetched(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", [12, "hello", True])
        self.storage.set("hey", "ho")

        # WHEN calling `get`
        value = self.storage.get("greeting")

        # THEN correct values is returned
        assert value == [12, "hello", True]

    def test_get__exists_but_expired__none_is_returned(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", "hello", ttl=10)
        self.storage.set("hey", "ho")

        # WHEN waiting 11 seconds and calling `get`
        with freeze_time(self.now + self.seconds(11)):
            value = self.storage.get("greeting")

        # THEN correct values is returned
        assert value is None

    def test_get__does_not_exist__is_not_fetched(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", [12, "hello", True])
        self.storage.set("hey", "ho")

        # WHEN calling `get` with unknown name
        # THEN correct value is returned
        assert self.storage.get("hello?") is None

    #
    # GET_ALL
    #
    def test_get_all__empty__fetches_none(self):

        # GIVEN base storage which is empty
        # WHEN calling `get_all`
        # THEN correct value is returned
        assert self.storage.get_all() == {}

    def test_get_all__non_empty__fetches_all(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", [12, "hello", True])
        self.storage.set("hey", "ho")

        # WHEN calling `get_all`
        # THEN correct value is returned
        assert self.storage.get_all() == {
            "greeting": [12, "hello", True],
            "hey": "ho",
        }

    def test_get_all__deletes_expired__fetches_all(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", [12, "hello", True])
        self.storage.set("hey1", "ho1", ttl=8)
        self.storage.set("hey2", "ho2", ttl=1)
        self.storage.set("hey3", "ho3", ttl=1)

        # WHEN waiting 6 seconds calling `get_all`
        # THEN correct value is returned
        with freeze_time(self.now + self.seconds(6)):
            assert self.storage.get_all() == {
                "greeting": [12, "hello", True],
                "hey1": "ho1",
            }

    #
    # EXISTS
    #
    def test_exists__exists__returns_true(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", [12, "hello", True])
        self.storage.set("hey", "ho")

        # WHEN calling `exists`
        # THEN correct value is returned
        assert self.storage.exists("hey") is True

    def test_exists__does_not_exist__returns_false(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", [12, "hello", True])
        self.storage.set("hey", "ho")

        # WHEN calling `exists` on unknown `name`
        # THEN correct value is returned
        assert self.storage.exists("hey?") is False

    def test_exists__expired__returns_false(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", [12, "hello", True])
        self.storage.set("hey", "ho", ttl=8)

        # WHEN waiting 10 seconds calling `exists`
        # THEN correct value is returned
        with freeze_time(self.now + self.seconds(9)):
            assert self.storage.exists("hey") is False

    #
    # EXPIRES_IN_SECONDS
    #
    def test_expires_in__exists_but_no_ttl__returns_true(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", [12, "hello", True])
        self.storage.set("hey", "ho")

        # WHEN calling `expires_in`
        # THEN correct value is returned
        assert self.storage.expires_in("hey") is None

    def test_expires_in__exists_with_ttl__returns_true(self):

        with freeze_time(self.now):
            # GIVEN base storage and some names being set
            self.storage.set("greeting", [12, "hello", True])
            self.storage.set("hey", "ho", ttl=10)

            # WHEN calling `expires_in`
            # THEN correct value is returned
            assert self.storage.expires_in("hey") == 10

    def test_expires_in__does_not_exist__returns_false(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", [12, "hello", True])
        self.storage.set("hey", "ho")

        # WHEN calling `expires_in` with unknown `name`
        # THEN correct value is returned
        assert self.storage.expires_in("hey?") is None

    def test_expires_in__expired__returns_false(self):

        # GIVEN base storage and some names being set
        self.storage.set("greeting", [12, "hello", True])
        self.storage.set("hey", "ho", ttl=10)

        # WHEN calling `expires_in`
        # THEN correct value is returned
        with freeze_time(self.now + self.seconds(11)):
            assert self.storage.expires_in("hey") is None

    #
    # DELETE
    #
    def test_delete__exists__deletes(self):

        # GIVEN base storage
        self.storage.set("greeting", "hello")
        self.storage.set("what", "hey")

        # WHEN calling `delete`
        self.storage.delete("what")

        # THEN correct values is delete
        assert self.storage.component.storage == {"greeting": '"hello"|'}

    def test_delete__does_not_exist__returns_true(self):

        # GIVEN base storage
        self.storage.set("greeting", "hello")
        self.storage.set("what", "hey")

        # WHEN calling `delete` with unknown `name`
        self.storage.delete("what?")

        # THEN correct values is delete
        assert self.storage.component.storage == {
            "greeting": '"hello"|',
            "what": '"hey"|',
        }
