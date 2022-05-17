import os
import time
import tempfile
import warnings
import traceback

import nostalgic


def post_test_clean_up():
    """Run after each test."""
    # clear singleton so that runs are separate
    nostalgic.Configuration._SingletonMetaclass__reset()


class TestSetting:

    def test_instance(self):
        my_setting = nostalgic.Setting('frobnitz')
        assert isinstance(my_setting, object)

    def test_key(self):
        my_setting = nostalgic.Setting("frobnitz")
        assert hasattr(my_setting, 'key')

        assert my_setting.key == 'frobnitz'

    def test_value(self):
        my_setting = nostalgic.Setting('frobnitz')
        assert hasattr(my_setting, 'value')
        assert hasattr(my_setting, '_default')

        other_setting = nostalgic.Setting('foo', default=42)
        assert other_setting.value == 42

        other_setting.value = 100
        assert other_setting.value == 100

    def test_getter(self):
        my_setting = nostalgic.Setting('frobnitz', default=24)
        assert hasattr(my_setting, 'getter')

        self.fake_ui_element = 42
        def custom_getter():
            return self.fake_ui_element

        other_setting = nostalgic.Setting('foo', default=100)
        assert other_setting.value == 100
        try:
            other_setting.getter() == 100
        except TypeError:
            pass
        else:
            raise AssertionError("No getter assigned. Should throw TypeError.")

        custom_getter_setting = nostalgic.Setting('bar', getter=custom_getter, default=200)
        assert custom_getter_setting.value == 200
        assert custom_getter_setting.getter() == 42

    def test_setter(self):
        my_setting = nostalgic.Setting('frobnitz')
        assert hasattr(my_setting, 'setter')

        self.fake_ui_element = 0
        def custom_setter(value):
            self.fake_ui_element = value

        other_setting = nostalgic.Setting('foo', default=24)
        assert other_setting.value == 24
        try:
            other_setting.setter(100)
        except TypeError:
            pass
        else:
            raise AssertionError("No setter assigned.  Should throw TypeError.")

        next_setting = nostalgic.Setting('bar', setter=custom_setter, default=24)

        assert next_setting.value == 24
        assert self.fake_ui_element == 0

        next_setting.setter(100)

        assert next_setting.value == 24
        assert self.fake_ui_element == 100


class TestConfiguration:

    ##########
    # object #
    ##########
    def test_instance(self):
        my_configuration = nostalgic.Configuration()
        assert isinstance(my_configuration, object)

    def test_singleton(self):
        my_configuration = nostalgic.Configuration()
        my_other_settings = nostalgic.Configuration()

        assert my_configuration == my_other_settings

    ###########
    # methods #
    ###########
    def test_add_setting(self):
        my_configuration = nostalgic.Configuration()

        assert hasattr(my_configuration, 'add_setting')
        assert callable(my_configuration.add_setting)

        my_configuration.add_setting("foo")
        assert isinstance(my_configuration['foo'], nostalgic.Setting)

    def test_default_save_location(self):
        my_configuration = nostalgic.Configuration()

        home_directory = os.path.expanduser('~')
        default_save_location = os.path.join(home_directory, 'test_nostalgic_config')
        assert my_configuration.config_file == default_save_location

    def test_custom_save_location(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            my_configuration = nostalgic.Configuration(temp_file.name)

        assert my_configuration.config_file == temp_file.name

    def test_read(self):
        # reading sets the Setting's value and also calls the
        # Setting's setter

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test")

            with open(temp_file, 'w', encoding='utf-8') as f:
                test_config = "[General]\nfirst = 1\nsecond = \"two\"\nthird = 42\nforth = \"four\""
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

            assert my_configuration.first == 1
            assert my_configuration.second == "two"

            # test whether setter gets called
            assert 'third' not in my_configuration._settings

            self.fake_ui_element = 0
            def custom_setter(value):
                self.fake_ui_element = value

            my_configuration.add_setting('third', setter=custom_setter)

            assert my_configuration.third is None
            assert self.fake_ui_element == 0

            my_configuration.read()

            assert my_configuration.third == 42
            assert self.fake_ui_element == 42

            assert 'fourth' not in my_configuration._settings

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
        assert text == "[General]\nfirst = 1\nsecond = \"two\"\n\n"

        def custom_getter():
            return 42

        my_configuration.add_setting("third", default=0, getter=custom_getter)
        assert my_configuration.third == 0

        my_configuration.write()

        with open(my_configuration.config_file, 'r', encoding='utf-8') as f:
            text = f.read()

        assert text == "[General]\nfirst = 1\nsecond = \"two\"\nthird = 42\n\n"
        assert my_configuration.third == 42

        # Clean up
        # NOTE: Clean up won't happen on failure
        os.remove(my_configuration.config_file)
        os.rmdir(temp_dir)

    ######################
    # Settings interface #
    ######################
    def test_settings_access(self):
        my_configuration = nostalgic.Configuration()

        def custom_getter():
            pass

        def custom_setter(value):
            pass

        my_configuration.add_setting("foo", getter=custom_getter, setter=custom_setter)
        assert my_configuration['foo'].getter == custom_getter
        assert my_configuration['foo'].setter == custom_setter

    def test_setting_value_access(self):
        my_configuration = nostalgic.Configuration()

        my_configuration.add_setting("foo", default="bar")
        assert my_configuration.foo == "bar"

        my_configuration.foo = 42

        # check that the setting hasn't simply been replaced by an int
        assert isinstance(my_configuration['foo'], nostalgic.Setting)
        assert my_configuration.foo == 42

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

        # the context above raised the warning to an error, causing
        # the setting to not be added. Redo now that the warning is no
        # longer considered an error
        my_configuration.add_setting("add_setting", default="banana")

        # shadowed methods return the method, not the Setting
        assert my_configuration.add_setting == nostalgic.Configuration().add_setting

        # if the user wants to shadow a method, they can reach into
        # the _settings dict
        assert my_configuration._settings['add_setting'].value == "banana"


if __name__ == '__main__':

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
    ]

    tests_to_skip = [
        # test_suites['configuration'].test_read,
        # test_suites['configuration'].test_write,
    ]

    tests_to_run = [test for test in tests_to_run if test not in tests_to_skip]

    failed = 0
    start = time.time()

    ONLY_SHOW_FAILS = True

    # NOTE: tests run in alphabetical ordering.  Introspect the code
    # to get the order they're declared in.
    for test in tests_to_run:
        if not ONLY_SHOW_FAILS: print(f"----------", flush=True)

        try:
            if not ONLY_SHOW_FAILS: print(f"  Running: {test.__name__}", flush=True)
            test()
            if not ONLY_SHOW_FAILS: print(f"  [PASS]", flush=True)
        except Exception as ex:
            failed += 1
            print(f"  [FAIL]: {test.__self__.__class__.__name__}.{test.__name__}\n{ex}", flush=True)
            print(f"{traceback.format_exc()}", flush=True)

        post_test_clean_up()

    stop = time.time()
    elapsed = stop-start
    print(f"----------", flush=True)
    if ONLY_SHOW_FAILS and failed == 0:
        print(f"  [PASS]", flush=True)

    print(f"Success:{len(tests_to_run)-failed}", flush=True)
    print(f"Fail:\t{failed} ", flush=True)
    print(f"Total:\t{len(tests_to_run)}\tTime: {(elapsed/60):.0f}:{(elapsed%60):.0f}", flush=True)
