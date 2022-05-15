# every setting must be declared

# getter used for syncing the Settings with the user interface
# setter used to sync the user interface with the Settings
# default is the default value

# getter and setter must be callables
# default must be a value
import os
import warnings


def show_only_warning_message(msg, *args, **kwargs):
    # the default warning behavior also shows a line of source code
    # See: https://stackoverflow.com/a/2187390
    return str(msg) + '\n'

warnings.formatwarning = show_only_warning_message


class ShadowWarning(UserWarning):
    pass


class Setting:

    def __init__(self, key, default=None, getter=None, setter=None):

        self.key      = key
        self._default = default
        self.value   = self._default
        self.getter   = getter
        self.setter   = setter

        if not self.getter:
            self.getter = self._default_value_getter

        if not setter:
            self.setter = self._default_value_setter

    def _default_value_getter(self):
        return self.value

    def _default_value_setter(self, value):
        self.value = value


class SingletonMetaclass(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMetaclass._instances:
            SingletonMetaclass._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMetaclass._instances[cls]

    def __reset(cls):
        """Delete the instance.

        Used for testing.

        Call as:

          nostalgic.Configuration._SingletonMetaclass__reset()

        """

        try:
            del SingletonMetaclass._instances[cls]
        except KeyError:
            pass


class Configuration(metaclass=SingletonMetaclass):

    def __init__(self, filename=os.path.expanduser('~')):
        super().__init__()

        # must define this way since we're overriding __setattr__
        self.__dict__['_settings'] = {}

        # Default Settings
        self.add_setting('configuration_file', filename)

    def add_setting(self, key, default=None, getter=None, setter=None):
        # WARNING: Clobbers extant Setting with same key!
        setting = Setting(key, default=default, getter=getter, setter=setter)
        self.__dict__['_settings'][key] = setting

    def __getitem__(self, key):
        return self.__dict__['_settings'][key]

    def __getattr__(self, name):
        return self.__dict__['_settings'][name].value

    def __getattribute__(self, name):
        if name in Configuration.__dict__ and name[:2] != '__':
            warnings.warn(f"[WARNING]: Setting '{name}' shadows a bound method of the same name!", ShadowWarning)
        return object.__getattribute__(self, name)
