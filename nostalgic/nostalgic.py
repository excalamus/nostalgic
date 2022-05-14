# every setting must be declared

# getter used for syncing the Settings with the user interface
# setter used to sync the user interface with the Settings
# initial is the initial value

# getter and setter must be callables
# initial must be a value
import os


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

    def _default_getter(self, name):
        return self.__dict__['_values'][name]

    def _default_setter(self, name, value):
        self.__dict__['_values'][name] = value

    def add_setting(self, key, getter=None, setter=None, initial=None):

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

    def __getattr__(self, name):
        if name in self._values:
            return self._values[name]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no setting '{name}'")

    def __setattr__(self, name, value):
        if name in self._values:
            self._values[name] = value
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no setting '{name}'")

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

    # TODO implement remaining "(python) Emulating container types"
