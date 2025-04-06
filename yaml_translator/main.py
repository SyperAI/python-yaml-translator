import typing
from pathlib import Path
from typing import Tuple, Any

import yaml

def dict_depth(d):
    if not isinstance(d, dict) or not d:
        return 0
    return 1 + max((dict_depth(v) for v in d.values() if isinstance(v, dict)), default=0)


class DeepDict(dict):
    def __init__(self, dict_):
        super().__init__(dict_)

    def __getitem__(self, key):
        item = None
        max_depth = dict_depth(self)
        keys = key.split(':')

        if len(keys) > max_depth:
            raise KeyError(f"Path is to deep. Your path is {len(keys)} keys, while given dict depth is {max_depth}")

        for key in keys:
            if item is None:
                item = super().__getitem__(key)
            else:
                item = item.__getitem__(key)
        return item

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


class Translation:
    _translations: dict[str, DeepDict] = {}

    def __repr__(self):
        return self._translations.__str__()

    def __init__(self, path: Path) -> None:
        for translation in path.iterdir():
            if translation.is_file() and translation.suffix == '.yaml':
                with open(translation, 'r', encoding='utf-8') as f:
                    self._translations[translation.stem] = DeepDict(yaml.safe_load(f))

    def get(self, path: str, language) -> typing.Any:
        return self._translations[language].get(path)

    def get_all(self, path: str) -> dict:
        translations = {}

        for language in self._translations.keys():
            translations[language] = self.get(path, language)

        return translations


class Translator:
    _translations = {}

    def __init__(self, translations_dir: str = "translations"):
        for translation_dir in Path(translations_dir).iterdir():
            if translation_dir.is_dir():
                self._translations[translation_dir.stem] = Translation(translation_dir)

    def get(self, group: str) -> Translation:
        return self._translations[group]

    def groups(self) -> tuple[Any, ...]:
        return tuple(self._translations.keys())


if __name__ == "__main__":
    translator = Translator()

    test_translation = translator.get("test")

    print(test_translation.get("post_removed_owner", "en"))
    print(test_translation.get_all("post_removed_owner"))
    print(translator.groups())


