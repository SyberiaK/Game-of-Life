from typing import Any

from util import util_funcs


class SettingsFileHandler:
    def __init__(self, file: str) -> None:
        self.file = file
        self.settings = {}

    def read_settings(self) -> None:
        with open(self.file, 'r') as f:
            buffer = f.read().strip().split('\n')

        for s in buffer:
            if s.startswith('#') or s == '':
                continue
            elif '=' not in s or ' ' in s:
                raise SFHWrongFileFormatting()

            var, val = s.split('=')
            if util_funcs.is_int(val):
                val = int(val)
            elif util_funcs.is_float(val):
                val = float(val)
            elif util_funcs.is_bytes(val):
                val = val[2:-1].encode()
            elif util_funcs.is_bool(val):
                val = util_funcs.str_to_bool(val)

            self.settings[var] = val
        print(self.settings)

    def get_setting(self, var: str) -> Any:
        if self.settings.get(var, None) is None:
            raise SFHSettingNotFound()
        return self.settings[var]

    def has_setting(self, var: str) -> Any:
        if self.settings.get(var, None) is None:
            return False
        return True

    def set_setting(self, var: str, val: Any) -> None:
        self.settings[var] = val

    def write_settings(self, comment: str = 'WARNING! Changing any of these strings manually can break things. '
                                            'Edit this file only if you know what you are doing.') -> None:
        with open(self.file, 'w') as f:
            if comment is not None:
                print(f'# {comment}\n', file=f)
            for key, val in self.settings.items():
                print(f'{key}={val}', file=f)

    def del_setting(self, var: str) -> None:
        if self.settings.get(var, None) is None:
            raise SFHSettingNotFound()
        del self.settings[var]

    def clear_settings(self) -> None:
        self.settings = {}


class SFHException(Exception):
    def __str__(self) -> str:
        return 'SettingsFileHandler exception message'


class SFHWrongFileFormatting(SFHException):
    def __str__(self) -> str:
        return 'wrong file formatting (are you sure the file is settings file?)'


class SFHSettingNotFound(SFHException):
    def __str__(self) -> str:
        return 'setting not found (are you sure you looked for correct setting name?)'
