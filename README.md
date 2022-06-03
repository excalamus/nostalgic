> ***Savor what you feel and what you see / Things that may not seem important now / But may be tomorrow***
>
> *–Chuck Schuldiner*

# Nostalgic
A drop-in configuration module to save and restore end-user and
application settings.

- No meta-files
- Built using only the Python standard library
- Handle UI syncing

# Install
```python
pip install nostalgic
```

# Motivation
Many configuration packages themselves require configuration files.
This often is extraneous.

Others provide a non-Pythonic API which hinders comprehension.  For
example, QSettings looks like

```python
# bad
self.settings.setValue("my_tracked_variable", value)
```

and

```python
# bad
self.settings.value("my_tracked_variable", DEFAULT_SETTINGS["my_tracked_variable"])
```

How you work with a variable depends on whether or not it's been
touched by Qt.

With Nostalgic, these calls look simply like

```python
# good
self.settings.my_tracked_value = value
```

and

```python
# good
self.settings.my_tracked_value
```

Furthermore, most applications likely require only a single
configuration.  Nostalgic uses a Configuration singleton for this
reason.  Instantiate a Configuration and the next time one is created,
it will be a reference to the already extant Configuration.  This
means explicit references to the Configuration don't need to be passed
around.

# Quick Start
A Configuration is a collection of Settings.

- Use a dot to get the Setting value (like an attribute)
- Settings can have a default initial value
- `write()` settings to disk and `read()` them back in

```python
# basic usage
import os   # needed only for demonstration
import sys  # needed only for demonstration
import nostalgic


if __name__ == '__main__':
    # create configuration in current directory
    cfg = nostalgic.Configuration("sample_config")

    # declare a setting 'foo' with initial value
    cfg.add_setting("foo", default="bar")

    print(cfg.foo)  # "bar"

    # change the value
    cfg.foo = "baz"

    try:
        # second run
        cfg.read()
        print("Config just read")
        print(cfg.foo)  # "baz"
        os.remove(cfg.config_file)
        if not os.path.exists(cfg.config_file):
            print("Removed config file")
    except FileNotFoundError:
        # first run, no config yet
        cfg.write()
        print("Wrote config")
        sys.exit()

```

```sh
$ python3 "/home/ahab/Projects/nostalgic/scratch/sample1.py"
bar
Wrote config

$ python3 "/home/ahab/Projects/nostalgic/scratch/sample1.py"
bar
Config just read
baz
Removed config file
```

## Advanced: coordinate a configuration with the UI
Optional setter and getter functions handle updating other parts of your code.

```python
# demonstrate getting on write() and setting on read()
import os   # needed only for demonstration
import sys  # needed only for demonstration
import nostalgic


class SettingsUI:

    def __init__(self):
        self.some_ui_thing_the_end_user_uses = 0


class Main:

    def __init__(self):
        self.cfg = nostalgic.Configuration("sample_config")
        self.settings_ui = SettingsUI()

        self.cfg.add_setting(
            "ui_related_thing",
            setter=self.custom_setter,  # called on read()
            getter=self.custom_getter)  # called on write()

    def custom_setter(self, value):
        print(f"Setting some_ui_thing_the_end_user_uses")
        self.settings_ui.some_ui_thing_the_end_user_uses = value

    def custom_getter(self):
        print(f"Getting some_ui_thing_the_end_user_uses")
        return self.settings_ui.some_ui_thing_the_end_user_uses


if __name__ == '__main__':
    main = Main()

    print(f"some_ui_thing_the_end_user_uses: "
          f"{main.settings_ui.some_ui_thing_the_end_user_uses}")  # 0, the initial value

    try:
        # second run
        main.cfg.read()
        print("Config just read")
        print(f"some_ui_thing_the_end_user_uses: "
              f"{main.settings_ui.some_ui_thing_the_end_user_uses}")
        os.remove(main.cfg.config_file)
        if not os.path.exists(main.cfg.config_file):
            print("Removed config file")
    except FileNotFoundError:
        # first run, no config yet

        # user changed the UI thing
        main.settings_ui.some_ui_thing_the_end_user_uses = 42
        main.cfg.write()
        print("Wrote config")
        sys.exit()

```

The first run gets the end-user value before writing:

```sh
$ python3 "/home/ahab/Projects/nostalgic/scratch/sample2.py"
some_ui_thing_the_end_user_uses: 0
Getting some_ui_thing_the_end_user_uses
Wrote config
```

The second run sets the end-user's previous value:

```sh
$ python3 "/home/ahab/Projects/nostalgic/scratch/sample2.py"
some_ui_thing_the_end_user_uses: 0
Setting some_ui_thing_the_end_user_uses
Config just read
some_ui_thing_the_end_user_uses: 42
Removed config file

```

Use `Configuration.set()` and `Configuration.get()` to apply or update
settings en masse without accessing the hard disk.

# Notes
- Shadowing Configuration methods with Settings of the same name is
  possible, although not recommended.  A warning will be given.

# Development
Install as "editable" using `pip`:

```sh
~$ cd Projects/nostalgic
~/Projects/nostalgic$ python3 -m venv venv
~/Projects/nostalgic$ source venv/bin/activate
(venv) ~/Projects/nostalgic$ pip install -e .
```

## Testing
Run tests using:

```sh
(venv) ~/Projects/nostalgic$ python3 tests/test_nostalgic.py
```
