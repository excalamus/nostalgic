# every setting must be declared

# getter used for syncing the Settings with the user interface
# setter used to sync the user interface with the Settings
# default is the default value

# getter and setter must be callables
# default must be a value
import os
import sys
import warnings


def show_only_warning_message(msg, *args, **kwargs):
    # the default warning behavior shows a superfluous line of code
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

    def __init__(self, filename=None):
        super().__init__()

        # must define this way since we're overriding __setattr__
        self.__dict__['_settings'] = {}

        # Default Settings
        if filename is None:
            home_directory = os.path.expanduser('~')
            calling_module = os.path.basename(sys.argv[0]).split('.')[0]
            config_file    = calling_module + "_settings"
            filename       = os.path.join(home_directory, config_file)

        self.add_setting('configuration_file', filename)

    def __getitem__(self, key):
        return self.__dict__['_settings'][key]

    def __getattr__(self, name):
        return self.__dict__['_settings'][name].value

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    def add_setting(self, key, default=None, getter=None, setter=None):
        # WARNING: Clobbers extant Setting with same key!
        setting = Setting(key, default=default, getter=getter, setter=setter)
        if key in Configuration.__dict__ and key[:2] != '__':
            warnings.warn(f"[WARNING]: Setting '{key}' shadows a bound method of the same name!", ShadowWarning)
        self.__dict__['_settings'][key] = setting

    def write(self):
        pass
