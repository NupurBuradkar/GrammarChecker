"""
User Custom Dictionary Module
Allows adding, removing, and checking words in the user's custom dictionary.
Persisted in user_dictionary.json.
"""

import json
import os
from typing import Set

DICTIONARY_FILE = os.path.join(os.path.dirname(__file__), "user_dictionary.json")


class UserDictionary:
    def __init__(self, storage_path: str = DICTIONARY_FILE):
        self.storage_path = storage_path
        self._words: Set[str] = set()
        self.load()

    def load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._words = set(w.strip().lower() for w in data if isinstance(w, str))
            except Exception:
                self._words = set()
        else:
            self._words = set()

    def save(self):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(sorted(list(self._words)), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving user dictionary: {e}")

    def add_word(self, word: str) -> bool:
        clean = word.strip().lower()
        if clean:
            self._words.add(clean)
            self.save()
            return True
        return False

    def remove_word(self, word: str) -> bool:
        clean = word.strip().lower()
        if clean in self._words:
            self._words.remove(clean)
            self.save()
            return True
        return False

    def contains(self, word: str) -> bool:
        return word.strip().lower() in self._words

    def get_all(self) -> list[str]:
        return sorted(list(self._words))


# Singleton instance
user_dict = UserDictionary()
