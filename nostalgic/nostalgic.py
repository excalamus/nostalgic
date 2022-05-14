# every setting must be declared

# getter used for syncing the Settings with the user interface
# setter used to sync the user interface with the Settings
# initial is the initial value

# getter and setter must be callables
# initial must be a value
import os


class Setting:

    def __init__(self, key, default=None, getter=None, setter=None):

        self.key      = key
        self._default = default
        self.value    = self._default
        self.getter   = getter
        self.setter   = setter

        if not self.getter:
            self.getter = self._default_getter

        if not setter:
            self.setter = self._default_setter

    def _default_getter(self):
        return self.value

    def _default_setter(self, value):
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
        self.__dict__['_filename'] = filename
        self.__dict__['_proxy']  = {}
        self.__dict__['_values'] = {}

    def _default_getter(self, key):
        return self.__dict__['_values'][key]

    def _default_setter(self, key, value):
        self.__dict__['_values'][key] = value

    def add_setting(self, key, getter=None, setter=None, initial=None):

        setting = Setting(key, getter, setter, initial)

        if not getter:
            getter = self._default_getter

        if not setter:
            setter = self._default_setter

        self._proxy[key] = {
            'getter' : getter,
            'setter' : setter,
            'initial': initial,
        }

        self._values[key] = initial

    def __getattr__(self, key):
        if key in self._values:
            return self._values[key]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no setting '{key}'")

    def __setattr__(self, key, value):
        if key in self._values:
            self._values[key] = value
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no setting '{key}'")

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        if key in self._values:
            self._values[key] = value
        else:
            raise KeyError(f"'{type(self).__name__}' object has no setting '{key}'")

    def __contains__(self, item):
        if item in self._values:
            return True

    def __len__(self):
        return len(self._values)
