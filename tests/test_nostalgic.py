# test_nostalgic.py – Test suite for Nostalgic
#
# Run tests with
#
#   python test_nostalgic.py
#
# See main() for run options.
#
# NOTE: There isn't an easy way to make an assert statement show what
# the expected value was using Python.  The only way is to write it
# manually.
#
# The following are Emacs Evil mode macros to automate writing the
# expected value.  The first macro is assigned to "@a". It looks for
# the next expression between "assert" and "==" and places it at the
# end of the occurring line after a comma.  The second macro is
# assigned to "@c" and works on the current line.
#
# See: https://stackoverflow.com/a/22820324
#
# Local Variables:
# eval: (evil-set-register ?a [?/ ?= ?= return ?? ?a ?s ?s ?e ?r ?t return ?w ?\C-v ?/ ?= ?= return ?g ?e ?y ?A ?, ?  escape ?p])
# eval: (evil-set-register ?c [?0 ?w ?w ?\C-v ?/ ?= ?= return ?g ?e ?y ?A ?, ?  escape ?p])
# End:

import os
import time
import tempfile
import warnings
import traceback

import nostalgic


def main():
    # Run options:
    ONLY_SHOW_FAILS = True
    BREAK_ON_FIRST_FAIL = True

    test_suites = {
        'setting': TestSetting(),
        'configuration': TestConfiguration(),
    }

    test_functions = [
        getattr(suite, m)
        for suite in test_suites.values()
        for m in dir(suite)
        if m[:4] == 'test'
    ]

    tests_to_run = [
        *test_functions,
        # test_suites['setting'].test_setter,
        # test_suites['setting'].test_getter,
        # test_suites['configuration'].test_setting_value_access,
        # test_suites['configuration'].test_custom_save_location,
        # test_suites['configuration'].test_read,
        # test_suites['configuration'].test_write,
        # test_suites['configuration'].test_add_setting,
    ]

    tests_to_skip = [
        # test_suites['configuration'].test_read,
        # test_suites['configuration'].test_write,
    ]

    tests_to_run = [test for test in tests_to_run if test not in tests_to_skip]

    tests_failed = 0
    tests_passed = 0
    tests_run = 0
    start = time.time()

    # NOTE: tests run in alphabetical ordering not in declared ordered.
    # Introspect the code to get the order they're declared in.
    for test in tests_to_run:
        tests_run += 1
        if not ONLY_SHOW_FAILS: print(f"----------", flush=True)

        try:
            if not ONLY_SHOW_FAILS: print(f"  Running: {test.__name__}", flush=True)
            test()
            if not ONLY_SHOW_FAILS: print(f"  [PASS]", flush=True)
            tests_passed += 1
        except Exception as ex:
            tests_failed += 1
            print(f"  [FAIL]: {test.__self__.__class__.__name__}.{test.__name__}\n{ex}", flush=True)
            print(f"{traceback.format_exc()}", flush=True)
            if BREAK_ON_FIRST_FAIL: break

        post_test_clean_up()

    stop = time.time()
    elapsed = stop-start
    print(f"----------", flush=True)
    if ONLY_SHOW_FAILS and tests_failed == 0:
        print(f"  [PASS]", flush=True)

    print(f"Success:{tests_passed}", flush=True)
    print(f"Fail:\t{tests_failed} ", flush=True)
    print(f"Total:\t{tests_passed + tests_failed}\tTime: {(elapsed/60):.0f}:{(elapsed%60):.0f}", flush=True)


def post_test_clean_up():
    """Run after each test."""
    # clear singleton so that runs are separate
    nostalgic.Configuration._SingletonMetaclass__reset()


class TestSetting:

    def test_key(self):
        my_setting = nostalgic.Setting("frobnitz")
        assert hasattr(my_setting, 'key')

        assert my_setting.key == 'frobnitz', my_setting.key

    def test_value(self):
        my_setting = nostalgic.Setting('frobnitz')
        assert hasattr(my_setting, 'value')
        assert hasattr(my_setting, '_default')

        other_setting = nostalgic.Setting('foo', default=42)
        assert other_setting.value == 42, other_setting.value

        other_setting.value = 100
        assert other_setting.value == 100, other_setting.value

    def test_setter(self):
        my_setting = nostalgic.Setting('frobnitz')
        assert hasattr(my_setting, 'setter')

        self.fake_ui_element = 0
        def custom_setter(value):
            self.fake_ui_element = value

        other_setting = nostalgic.Setting('foo', default=24)
        assert other_setting.value == 24, other_setting.value
        try:
            other_setting.setter(100)
        except TypeError:
            pass
        else:
            raise AssertionError("No setter assigned.  Should throw TypeError.")

        next_setting = nostalgic.Setting('bar', setter=custom_setter, default=24)

        assert next_setting.value == 24, next_setting.value
        assert self.fake_ui_element == 0, self.fake_ui_element

        next_setting.setter(100)

        assert next_setting.value == 24, next_setting.value
        assert self.fake_ui_element == 100, self.fake_ui_element

    def test_getter(self):
        my_setting = nostalgic.Setting('frobnitz', default=24)
        assert hasattr(my_setting, 'getter')

        self.fake_ui_element = 42
        def custom_getter():
            return self.fake_ui_element

        other_setting = nostalgic.Setting('foo', default=100)
        assert other_setting.value == 100, other_setting.value
        try:
            other_setting.getter() == 100
        except TypeError:
            pass
        else:
            raise AssertionError("No getter assigned. Should throw TypeError.")

        custom_getter_setting = nostalgic.Setting('bar', getter=custom_getter, default=200)
        assert custom_getter_setting.value == 200, custom_getter_setting.value
        assert custom_getter_setting.getter() == 42, custom_getter_setting.getter()


class TestConfiguration:

    ########################
    # Configuration object #
    ########################
    def test_singleton(self):
        my_configuration = nostalgic.Configuration()
        my_other_settings = nostalgic.Configuration()

        assert my_configuration == my_other_settings, my_configuration

    def test_default_save_location(self):
        my_configuration = nostalgic.Configuration()

        home_directory = os.path.expanduser('~')
        default_save_location = os.path.join(home_directory, 'test_nostalgic_config')
        assert my_configuration.config_file == default_save_location, my_configuration.config_file

    def test_custom_save_location(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            my_configuration = nostalgic.Configuration(temp_file.name)

        assert my_configuration.config_file == temp_file.name, my_configuration.config_file

    ######################
    # Settings interface #
    ######################
    def test_setting_value_access(self):
        my_configuration = nostalgic.Configuration()

        my_configuration.add_setting("foo", default="bar")
        assert my_configuration.foo == "bar", my_configuration.foo

        my_configuration.foo = 42

        # check that the setting hasn't simply been replaced by an int
        assert isinstance(my_configuration['foo'], nostalgic.Setting)
        assert my_configuration.foo == 42, my_configuration.foo

        # NOTE: How should we handle the edge case where a user
        # creates a Setting whose key is the same as a Configuration
        # method?  With the implementation at the time of writing
        # (using __getattr__ to return Setting values), you might
        # expect the Setting to clobber the method. It turns out
        # that's not the case–the method takes precedence.  Is it
        # worth the time to correct that for the sake of conceptual
        # purity?  Probably not. Instead, throw a warning to let the
        # developer know and document the design.  Test to make sure
        # that this "default behavior" doesn't change from beneath us.
        #
        # See: https://tenthousandmeters.com/blog/python-behind-the-scenes-7-how-python-attributes-work/
        with warnings.catch_warnings() as w:
            warnings.filterwarnings("error")
            try:
                my_configuration.add_setting("add_setting", default="banana")
            except nostalgic.ShadowWarning:
                pass
            else:
                raise AssertionError("Shadowing a bound method does not raise a warning!")

        # the context above elevated the warning to an error, causing
        # the setting to not be added. Redo now that the warning is no
        # longer considered an error
        my_configuration.add_setting("add_setting", default="banana")

        # shadowed methods return the method, not the Setting
        assert my_configuration.add_setting == nostalgic.Configuration().add_setting, my_configuration.add_setting

        # if the user wants to shadow a method, they can reach into
        # the _settings dict
        assert my_configuration._settings['add_setting'].value == "banana", my_configuration._settings['add_setting'].value

    def test_settings_object_access(self):
        my_configuration = nostalgic.Configuration()

        def custom_getter():
            pass

        def custom_setter(value):
            pass

        my_configuration.add_setting("foo", getter=custom_getter, setter=custom_setter)
        assert my_configuration['foo'].getter == custom_getter, my_configuration['foo'].getter
        assert my_configuration['foo'].setter == custom_setter, my_configuration['foo'].setter

    ###########
    # methods #
    ###########
    def test_add_setting(self):
        my_configuration = nostalgic.Configuration()

        assert hasattr(my_configuration, 'add_setting')
        assert callable(my_configuration.add_setting)

        my_configuration.add_setting("foo")
        assert isinstance(my_configuration['foo'], nostalgic.Setting)

        with warnings.catch_warnings() as w:
            warnings.filterwarnings("error")
            try:
                my_configuration.add_setting("foo", default="banana")
            except nostalgic.OverwriteWarning:
                pass
            else:
                raise AssertionError("Overwriting a setting does not raise a warning!")

    def test_read(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test")

            with open(temp_file, 'w', encoding='utf-8') as f:
                test_config = "[General]\nfirst = 1\nsecond = \"two\"\nthird = 42\nforth = \"four\"\nfifth = \"was set\""
                f.write(test_config)

            my_configuration = nostalgic.Configuration(temp_file)

            assert hasattr(my_configuration, 'read')
            assert callable(my_configuration.read)

            # only load declared Settings
            my_configuration.read()
            assert 'first' not in my_configuration._settings
            assert 'second' not in my_configuration._settings

            my_configuration.add_setting("first")
            my_configuration.add_setting("second")

            assert my_configuration.first is None
            assert my_configuration.second is None

            my_configuration.read()

            assert my_configuration.first == 1, my_configuration.first
            assert my_configuration.second == "two", my_configuration.second

            # test whether setter gets called by default
            assert 'third' not in my_configuration._settings

            self.fake_ui_element = 0
            def custom_setter(value):
                self.fake_ui_element = value

            my_configuration.add_setting('third', setter=custom_setter)

            assert my_configuration.third is None
            assert self.fake_ui_element == 0, self.fake_ui_element

            my_configuration.read()

            assert my_configuration.third == 42, my_configuration.third
            assert self.fake_ui_element == 42, self.fake_ui_element

            assert 'fourth' not in my_configuration._settings

            # test that calling setters can be disabled
            self.fifth_element = "not set"
            def set_fifth(value):
                self.fifth_element = value

            my_configuration.add_setting("fifth", default="default", setter=set_fifth)

            assert self.fifth_element == "not set", self.fifth_element
            assert my_configuration.fifth == "default", my_configuration.fifth

            my_configuration.read(sync=False)

            # only the configuration should have changed
            assert self.fifth_element == "not set", self.fifth_element
            assert my_configuration.fifth == "was set", my_configuration.fifth

    def test_write(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test")
            my_configuration = nostalgic.Configuration(temp_file)

            # make sure the test directory/file doesn't already exist
            assert not os.path.isdir(my_configuration.config_file)
            assert not os.path.exists(my_configuration.config_file)

            assert hasattr(my_configuration, 'write')
            assert callable(my_configuration.write)

            my_configuration.add_setting("first", default=1)
            my_configuration.add_setting("second", default="two")

            my_configuration.write()
            assert os.path.exists(my_configuration.config_file)

            with open(my_configuration.config_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # configparser writes putting two new lines at the end of the
            # file (one for the end line, one for end of file(?)).  I'm
            # not going to fight with that; just test for it.
            #
            # NOTE: we choose not to write the default settings
            # (e.g. config_file) to disk
            assert text == "[General]\nfirst = 1\nsecond = \"two\"\n\n", text

            def custom_getter():
                return 42

            my_configuration.add_setting("third", default=0, getter=custom_getter)
            assert my_configuration.third == 0, my_configuration.third

            my_configuration.write()

            with open(my_configuration.config_file, 'r', encoding='utf-8') as f:
                text = f.read()

            assert text == "[General]\nfirst = 1\nsecond = \"two\"\nthird = 42\n\n", text
            assert my_configuration.third == 42, my_configuration.third

            # test that calling getters can be disabled
            def getter_that_gets_disabled():
                return "getter called when it shouldn't have been"

            my_configuration.add_setting(
                "test_sync_disable",
                default="default",
                getter=getter_that_gets_disabled)

            assert my_configuration.test_sync_disable == "default", my_configuration.test_sync_disable

            my_configuration.write(sync=False)

            assert my_configuration.test_sync_disable == "default", my_configuration.test_sync_disable

            # Clean up
            # NOTE: Clean up won't happen on failure
            post_test_clean_up()
            os.remove(my_configuration.config_file)
            os.rmdir(temp_dir)

        # test that if the file doesn't already exist, it will be created
        non_temp_configuration = nostalgic.Configuration("test_config_file_right_here_please_delete")

        # if filename has no directory, then directory creation code
        # fails.  also, if the user gave the config_file relative to the
        # current directory, the current directory could change and a
        # second configuration be written. Prevent these by storing
        # absolute path.
        assert non_temp_configuration.config_file == os.path.abspath("test_config_file_right_here_please_delete"), non_temp_configuration.config_file

        assert not os.path.exists(non_temp_configuration.config_file), \
            (f"Config file '{non_temp_configuration.config_file}' exists when it should not. "
             f"Maybe it's left over from a failed run?  Delete it and try again.")

        non_temp_configuration.add_setting("test", default=True)

        warnings.warn(
            (f"[WARNING]: Created non-temp file: "
             f"'{os.path.abspath(non_temp_configuration.config_file)}'"))
        non_temp_configuration.write()

        assert os.path.exists(non_temp_configuration.config_file)

        with open(non_temp_configuration.config_file, 'r', encoding='utf-8') as f:
            text = f.read()

        assert text == "[General]\ntest = true\n\n", text

        # Clean up
        # NOTE: Clean up won't happen on failure
        os.remove(non_temp_configuration.config_file)
        if os.path.exists(non_temp_configuration.config_file):
            warnings.warn(f"[WARNING]: Failed to remove: '{non_temp_configuration.config_file}'")

    def test_get(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test")
            my_configuration = nostalgic.Configuration(temp_file)

            # test that get method exists
            assert hasattr(my_configuration, 'get')
            assert callable(my_configuration.get)

            # test that get takes a list of settings and calls their
            # getter
            self.element_1 = 42

            def get_element_1():
                return self.element_1

            my_configuration.add_setting("element_1", default=0, getter=get_element_1)

            assert self.element_1 == 42, self.element_1
            assert my_configuration.element_1 == 0, my_configuration.element_1

            my_configuration.get(["element_1"])

            assert my_configuration.element_1 == 42, my_configuration.element_1

            # test that settings are called separately
            self.element_1 = 24
            self.element_2 = 50

            def get_element_2():
                return self.element_2

            assert self.element_1 == 24, self.element_1
            assert self.element_2 == 50, self.element_2

            my_configuration.add_setting("element_2", default=0, getter=get_element_2)

            assert my_configuration.element_1 == 42, my_configuration.element_1
            assert my_configuration.element_2 == 0, my_configuration.element_2

            my_configuration.get(["element_2"])

            assert my_configuration.element_1 == 42, my_configuration.element_1
            assert my_configuration.element_2 == 50, my_configuration.element_2

            # test that multiple elements can be passed in
            self.element_2 = 10

            assert my_configuration.element_1 == 42, my_configuration.element_1
            assert my_configuration.element_2 == 50, my_configuration.element_2

            my_configuration.get(["element_1", "element_2"])

            assert my_configuration.element_1 == 24, my_configuration.element_1
            assert my_configuration.element_2 == 10, my_configuration.element_2

            # test that success returns the value before the get
            self.element_1 = 1
            self.element_2 = 2

            rv = my_configuration.get(["element_1", "element_2"])

            assert rv == {"element_1": 24, "element_2": 10}, rv
            assert my_configuration.element_1 == 1, my_configuration.element_1
            assert my_configuration.element_2 == 2, my_configuration.element_2

            # test that settings without getters don't cause problems
            my_configuration.add_setting("no_getter", default=0)

            assert my_configuration.no_getter == 0, my_configuration.no_getter

            rv = my_configuration.get(["no_getter"])

            assert rv == {}, rv

            # test that passing in nothing calls all getters
            self.element_1 = 1
            self.element_2 = 2

            my_configuration.get()

            assert my_configuration.element_1 == 1, my_configuration.element_1
            assert my_configuration.element_2 == 2, my_configuration.element_2

    def test_set(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test")
            my_configuration = nostalgic.Configuration(temp_file)

            # test that set method exists
            assert hasattr(my_configuration, 'set')
            assert callable(my_configuration.set)

            # test that set takes a list of settings and calls their
            # setter
            self.element_1 = 1

            def set_element_1(value):
                self.element_1 = value

            my_configuration.add_setting("element_1", default=0, setter=set_element_1)

            assert self.element_1 == 1, self.element_1
            assert my_configuration.element_1 == 0, my_configuration.element_1

            my_configuration.set(["element_1"])

            assert self.element_1 == 0, self.element_1
            assert my_configuration.element_1 == 0, my_configuration.element_1

            # test that settings are called separately
            self.element_1 = 1
            self.element_2 = 2

            def set_element_2(value):
                self.element_2 = value

            assert self.element_1 == 1, self.element_1
            assert self.element_2 == 2, self.element_2

            my_configuration.add_setting("element_2", default=0, setter=set_element_2)

            # adding settings sets default
            assert my_configuration.element_1 == 0, my_configuration.element_1
            assert my_configuration.element_2 == 0, my_configuration.element_2

            # adding a setting doesn't change the UI elements
            assert self.element_1 == 1, self.element_1
            assert self.element_2 == 2, self.element_2

            my_configuration.set(["element_2"])

            # calling set on element_2 doesn't affect element_1
            assert self.element_1 == 1, self.element_1
            assert self.element_2 == 0, self.element_2

            # test that multiple elements can be passed in

            # reset UI elements
            self.element_1 = 1
            self.element_2 = 2

            # confirm that the configuration is still in its default state
            assert my_configuration.element_1 == 0, my_configuration.element_1
            assert my_configuration.element_2 == 0, my_configuration.element_2

            my_configuration.set(["element_1", "element_2"])

            # confirm that the elements were set
            assert self.element_1 == 0, self.element_1
            assert self.element_2 == 0, self.element_2
            assert my_configuration.element_1 == 0, my_configuration.element_1
            assert my_configuration.element_2 == 0, my_configuration.element_2

            # test that settings without setters don't cause problems
            my_configuration.add_setting("no_setter", default=0)

            assert my_configuration.no_setter == 0

            assert my_configuration.set(["no_setter"]) == None

            # test that passing in nothing calls all setters
            self.element_1 = 1
            self.element_2 = 2

            my_configuration.set()

            assert self.element_1 == 0, self.element_1
            assert self.element_2 == 0, self.element_2


if __name__ == '__main__':
    main()
