from typing import Callable
from random import choices as _choices
import json

_charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-"
__all__ = ("IdManager", "Database")

_default = {
    "private_code": {}
}


class Database(dict[str, ...]):
    def __init__(self, filename: str):
        super(Database, self).__init__(_default)
        self._filename = filename

        try:
            with open(filename, "r", encoding="utf-8") as file:
                self.update(json.load(file))
        except FileNotFoundError:
            pass
        self._id_manager: IdManager = IdManager(self.get("private_code", None), self.save)
        self.save()

    def save(self) -> None:
        self["private_code"] = self._id_manager.to_data()
        with open(self._filename, "w", encoding="utf-8") as file:
            json.dump(self, file, indent=2, ensure_ascii=False)

    @property
    def id_manager(self):
        return self._id_manager


class IdManager:
    def __init__(self, data: dict[str, int] = None, save: Callable[[], None] = lambda: None):
        data = data or {}
        self._reversed: dict[str, int] = data.copy()
        self._default: dict[int, str] = {v: k for k, v in data.items()}
        self._save = save

    def to_data(self) -> dict[str, int]:
        return self._reversed.copy()

    def add(self, id: int) -> str:
        if id in self._default.keys():
            return self._default[id]
        codes = self._reversed.keys()
        while True:
            code = "".join(_choices(_charset, k=15))
            if code not in codes:
                break
        self._default[id] = code
        self._reversed[code] = id
        self._save()
        return code

    def get(self, key: str | int, default=None):
        if isinstance(key, int):
            return self._default.get(key, default)
        elif isinstance(key, str):
            return self._reversed.get(key, default)
        else:
            raise TypeError(f"key must be str or int not {type(key)}")

    def pop(self, key: str | int, default=None):
        if isinstance(key, int):
            k = self._default.pop(key, None)
            if k is None:
                return default
            del self._reversed[k]
            self._save()
        elif isinstance(key, str):
            k = self._reversed.pop(key, None)
            if k is None:
                return default
            del self._default[k]
            self._save()
        else:
            raise TypeError(f"key must be str or int not {type(key)}")

    def __getitem__(self, key: str | int) -> int | str:
        if isinstance(key, int):
            return self._default[key]
        elif isinstance(key, str):
            return self._reversed[key]
        else:
            raise TypeError(f"key must be str or int not {type(key)}")

    def __delitem__(self, key: str | int):
        if isinstance(key, int):
            k = self._default.pop(key)
            del self._reversed[k]
            self._save()
        elif isinstance(key, str):
            k = self._reversed.pop(key)
            del self._default[k]
            self._save()
        else:
            raise TypeError(f"key must be str or int not {type(key)}")
