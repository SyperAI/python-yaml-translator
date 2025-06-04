import typing
from pathlib import Path
from typing import Any

import yaml


def dict_depth(d: dict):
    """
    This function allows you to find the maximum depth of a given dictionary. Depth is the number of invested dictionaries.

    :param d: Any dictionary deep of which you need to find
    :return: Given dictionary depth
    """
    if not isinstance(d, dict) or not d:
        return 0
    return 1 + max((dict_depth(v) for v in d.values() if isinstance(v, dict)), default=0)


def rewrap(translations: dict) -> dict:
    result = {}
    for lang, entries in translations.items():
        if isinstance(entries, dict):
            for key, text in entries.items():
                result.setdefault(key, {})[lang] = text
        else:
            result[lang] = entries
    return result


def _format(dict_data: dict, format_values: dict) -> dict:
    """
    This function allows formatting on the specified data key in the dictionary with support of invested dictionaries.

    :param dict_data: Dictionary, Data in which you need to format.
    :param format_values: The keys to which formatting will occur and values that will be set in the form of a dictionary.
    :return: Given dictionary after formatting
    """
    if format_values is None:
        return dict_data

    result = {}
    for key, value in dict_data.items():
        if isinstance(value, dict):
            result[key] = _format(value, format_values)
        elif isinstance(value, str):
            result[key] = value.format(**format_values)
        else:
            result[key] = value

    return result


class DeepDict(dict):
    """
    Improved dictionary with support for obtaining data from invested dictionaries in 1 request
    """

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

    def get(self, key, default=None, format: dict = None) -> Any:
        """

        :param key:
        :param default: Value that will be returned if key is not in dict
        :param format: Pass if you want to format some values in dictionary. Must be dict where keys is format keys and
         values is values which will be replaced by the specified keys.
          The principle of operation is the same as the built-in .format() func of the str class
        :return:
        """

        try:
            if format is None:
                return self[key]
            else:
                return _format(self[key], format)
        except KeyError:
            return default


class Translation:
    """

    """

    _translations: dict[str, DeepDict] = {}

    def __repr__(self):
        return self._translations.__str__()

    def __init__(self, path: Path) -> None:
        for translation in path.iterdir():
            if translation.is_file() and translation.suffix == '.yaml' or translation.suffix == '.yml':
                with open(translation, 'r', encoding='utf-8') as f:
                    self._translations[translation.stem] = DeepDict(yaml.safe_load(f))

    def get(self, path: str, language: str, format: dict = None) -> typing.Any:
        """

        :param path:
        :param language:
        :param format:
        :return:
        """
        return self._translations[language].get(path, format=format)

    def get_all(self, path: str, format: dict = None) -> dict:
        translations = {}

        for language in self._translations.keys():
            translations[language] = self.get(path, language, format)

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
    pass
