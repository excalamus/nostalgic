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
        # test_suites['configuration'].test_get_calls_getters_separately,
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

    # NOTE: tests run in alphabetical ordering not in declared
    # ordered.  Either implement code introspection to get the order
    # they're declared in or declare the order explicitly in
    # tests_to_run.
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
            if BREAK_ON_FIRST_FAIL:
                print(f"BROKE ON FIRST FAIL", flush=True)
                break

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
    """Setting object test suite."""

    def test_has_key(self):
        foo_setting = nostalgic.Setting("foo")
        assert hasattr(foo_setting, 'key'), "Setting needs a 'key' attribute"

        assert foo_setting.key == "foo", foo_setting.key

    def test_has_value(self):
        foo_setting = nostalgic.Setting("foo")
        assert hasattr(foo_setting, 'value'), "Setting needs a 'value' attribute"

    def test_has_optional_default(self):
        foo_setting = nostalgic.Setting("foo")
        assert hasattr(foo_setting, '_default'), "Setting needs a '_default' attribute"

    def test_default_argument_sets_initial_value(self):
        foo_setting = nostalgic.Setting("foo", default="bar")
        assert foo_setting.value == "bar", foo_setting.value

    def test_value_independent_from_default(self):
        foo_setting = nostalgic.Setting("foo", default="bar")

        foo_setting.value = "baz"

        assert foo_setting.value == "baz", foo_setting.value
        assert foo_setting._default == "bar", foo_setting._default

    def test_has_optional_setter(self):
        foo_setting = nostalgic.Setting("foo")
        assert hasattr(foo_setting, "setter"), "Setting needs a 'setter' attribute"

    def test_setter_sets_external_variable_only(self):
        self.ui_element = "not set"

        def custom_setter(value):
            self.ui_element = value

        foo_setting = nostalgic.Setting("foo", default="foo default", setter=custom_setter)

        assert self.ui_element == "not set", self.ui_element
        assert foo_setting.value == "foo default", foo_setting.value

        foo_setting.setter("value was set")

        assert self.ui_element == "value was set", self.ui_element
        assert foo_setting.value == "foo default", foo_setting.value

    def test_has_optional_getter(self):
        foo_setting = nostalgic.Setting("foo")
        assert hasattr(foo_setting, "getter"), "Setting needs a 'getter' attribute"

    def test_getter_gets_external_variable_only(self):
        self.ui_element = "ui element value"

        def custom_getter():
            return self.ui_element

        foo_setting = nostalgic.Setting("foo", default="bar", getter=custom_getter)

        assert foo_setting.getter() == "ui element value", foo_setting.getter()
        assert foo_setting.value == "bar", foo_setting.value


class TestConfiguration:

    def test_only_a_single_configuration_object_can_be_made(self):
        my_config    = nostalgic.Configuration()
        other_config = nostalgic.Configuration()

        assert my_config == other_config, f"All configurations should be the same object\n{my_config=}\n{other_config=}"

    def test_default_save_location(self):
        my_config             = nostalgic.Configuration()
        home_directory        = os.path.expanduser('~')
        default_save_location = os.path.join(home_directory, 'test_nostalgic_config')

        assert my_config.config_file == default_save_location, my_config.config_file

    def test_custom_save_location(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            my_config = nostalgic.Configuration(temp_file.name)

            assert my_config.config_file == temp_file.name, my_config.config_file

    def test_has_add_setting_method(self):
        my_config = nostalgic.Configuration()

        assert hasattr(my_config, 'add_setting')
        assert callable(my_config.add_setting)

    def test_attribute_assignment_sets_setting_value(self):
        my_config = nostalgic.Configuration()
        my_config.add_setting("foo")

        my_config.foo = 42

        # check that the setting hasn't simply been replaced by an int
        assert isinstance(my_config["foo"], nostalgic.Setting)
        assert my_config.foo == 42, my_config.foo

    def test_add_setting__adds_a_setting_object(self):
        my_config = nostalgic.Configuration()

        my_config.add_setting("foo")
        assert isinstance(my_config.__dict__['_settings']["foo"], nostalgic.Setting)

    def test_add_setting__overwriting_setting_raises_warning(self):
        my_config = nostalgic.Configuration()
        my_config.add_setting("foo")

        with warnings.catch_warnings() as w:
            warnings.filterwarnings("error")
            try:
                my_config.add_setting("foo", default="banana")
            except nostalgic.OverwriteWarning:
                pass
            else:
                raise AssertionError("Overwriting a setting does not raise a warning!")

    def test_add_setting__shadow_class_method_with_setting_of_same_name_throws_warning(self):
        my_config = nostalgic.Configuration()

        with warnings.catch_warnings() as w:
            warnings.filterwarnings("error")
            try:
                my_config.add_setting("add_setting", default="banana")
            except nostalgic.ShadowWarning:
                pass
            else:
                raise AssertionError("Shadowing a bound method does not raise a warning!")

    def test_add_setting__shadow_class_method_with_setting_of_same_name_returns_method(self):
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
        my_config = nostalgic.Configuration()

        my_config.add_setting("add_setting", default="banana")

        # shadowed methods return the method, not the Setting
        assert my_config.add_setting == nostalgic.Configuration().add_setting, my_config.add_setting

        # if the user wants to shadow a method, they can reach into
        # the _settings dict to get the value
        assert my_config._settings['add_setting'].value == "banana", my_config._settings['add_setting'].value

    def test_add_setting__takes_optional_setter(self):
        my_config = nostalgic.Configuration()

        def custom_setter(value):
            pass

        my_config.add_setting("foo", setter=custom_setter)
        assert my_config["foo"].setter == custom_setter, my_config["foo"].setter

    def test_add_setting__takes_optional_getter(self):
        my_config = nostalgic.Configuration()

        def custom_getter():
            pass

        my_config.add_setting("foo", getter=custom_getter)
        assert my_config["foo"].getter == custom_getter, my_config["foo"].getter

    def test_has_read_method(self):
        my_config = nostalgic.Configuration()

        assert hasattr(my_config, 'read')
        assert callable(my_config.read)

    def test_read__loads_declared_settings_from_disk(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test")

            with open(temp_file, 'w', encoding='utf-8') as f:
                test_config = "[General]\nfirst = 1\nsecond = \"two\""
                f.write(test_config)

            my_config = nostalgic.Configuration(temp_file)

            my_config.read()

            # prove that nothing was read from disk into the
            # configuration
            assert 'first' not in my_config._settings
            assert 'second' not in my_config._settings

            my_config.add_setting("first")
            my_config.add_setting("second")

            # confirm that the newly added settings are blank
            assert my_config.first is None
            assert my_config.second is None

            my_config.read()

            # now that the settings are declared, they are read in
            assert my_config.first == 1, my_config.first
            assert my_config.second == "two", my_config.second

    def test_read__calls_setters_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test")

            with open(temp_file, 'w', encoding='utf-8') as f:
                test_config = "[General]\nthird = 42"
                f.write(test_config)

            my_config = nostalgic.Configuration(temp_file)

            self.fake_ui_element = 0

            def custom_setter(value):
                self.fake_ui_element = value

            my_config.add_setting('third', setter=custom_setter)

            assert my_config.third is None
            assert self.fake_ui_element == 0, self.fake_ui_element

            my_config.read()

            # confirm setting was read
            assert my_config.third == 42, my_config.third
            # confirm setter was called
            assert self.fake_ui_element == 42, self.fake_ui_element

    def test_read__can_disable_calling_setters(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test")

            with open(temp_file, 'w', encoding='utf-8') as f:
                test_config = "[General]\nfoo = \"was set\""
                f.write(test_config)

            my_config = nostalgic.Configuration(temp_file)

            # test that calling setters can be disabled
            self.ui_foo = "not set"
            def set_ui_foo(value):
                self.ui_foo = value

            my_config.add_setting("foo", default="default", setter=set_ui_foo)

            assert self.ui_foo == "not set", self.ui_foo
            assert my_config.foo == "default", my_config.foo

            my_config.read(sync=False)

            # only the configuration should have changed
            assert self.ui_foo == "not set", self.ui_foo
            assert my_config.foo == "was set", my_config.foo

    def test_has_write_method(self):
        my_config = nostalgic.Configuration()

        assert hasattr(my_config, 'write')
        assert callable(my_config.write)

    def test_write__saves_settings_to_disk(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test")
            my_config = nostalgic.Configuration(temp_file)

            # make sure the test directory/file doesn't already exist
            assert not os.path.isdir(my_config.config_file)
            assert not os.path.exists(my_config.config_file)

            my_config.add_setting("first", default=1)
            my_config.add_setting("second", default="two")

            my_config.write()

            # check that a file was created
            assert os.path.exists(my_config.config_file)

            # check file contents
            with open(my_config.config_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # configparser writes putting two new lines at the end of the
            # file (one for the end line, one for end of file(?)).  I'm
            # not going to fight with that; just test for it.
            #
            # NOTE: we choose not to write the default settings
            # (e.g. config_file) to disk
            assert text == "[General]\nfirst = 1\nsecond = \"two\"\n\n", text

    def test_write__calls_getters_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test")
            my_config = nostalgic.Configuration(temp_file)

            def custom_getter():
                return "baz"

            my_config.add_setting("foo", default="bar", getter=custom_getter)
            assert my_config.foo ==  "bar", my_config.third

            my_config.write()

            with open(my_config.config_file, 'r', encoding='utf-8') as f:
                text = f.read()

            assert text == "[General]\nfoo = \"baz\"\n\n", text
            assert my_config.foo == "baz", my_config.foo

    def test_write__can_disable_calling_getters(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test")
            my_config = nostalgic.Configuration(temp_file)

            def getter_that_gets_disabled():
                return "getter called when it shouldn't have been"

            my_config.add_setting(
                "test_sync_disable",
                default="default",
                getter=getter_that_gets_disabled)

            assert my_config.test_sync_disable == "default", my_config.test_sync_disable

            my_config.write(sync=False)

            assert my_config.test_sync_disable == "default", my_config.test_sync_disable

    def test_write__config_file_is_created_if_none_exists(self):
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

    def test_has_get_method(self):
        my_config = nostalgic.Configuration()

        assert hasattr(my_config, 'get')
        assert callable(my_config.get)

    def test_get__takes_list_of_settings_and_calls_their_getters(self):
        my_config = nostalgic.Configuration()

        self.ui_element_1 = "got 1"

        def get_element_1():
            return self.ui_element_1

        my_config.add_setting("element_1", default="not got 1", getter=get_element_1)

        assert self.ui_element_1 == "got 1", self.ui_element_1
        assert my_config.element_1 == "not got 1", my_config.element_1

        my_config.get(["element_1"])

        assert my_config.element_1 == "got 1", my_config.element_1

    def test_get__calls_getters_separately(self):
        my_config = nostalgic.Configuration()

        self.ui_element_1 = "got 1"
        self.ui_element_2 = "got 2"

        def get_element_1():
            return self.ui_element_1

        def get_element_2():
            return self.ui_element_2

        assert self.ui_element_1 == "got 1", self.ui_element_1
        assert self.ui_element_2 == "got 2", self.ui_element_2

        my_config.add_setting("element_1", default="not got 1", getter=get_element_1)
        my_config.add_setting("element_2", default="not got 2", getter=get_element_2)

        assert my_config.element_1 == "not got 1", my_config.element_1
        assert my_config.element_2 == "not got 2", my_config.element_2

        my_config.get(["element_2"])

        assert my_config.element_1 == "not got 1", my_config.element_1
        assert my_config.element_2 == "got 2", my_config.element_2

    def test_get__can_get_multiple_settings_at_once(self):
        my_config = nostalgic.Configuration()

        self.ui_element_1 = "got 1"
        self.ui_element_2 = "got 2"

        def get_element_1():
            return self.ui_element_1

        def get_element_2():
            return self.ui_element_2

        my_config.add_setting("element_1", default="not got 1", getter=get_element_1)
        my_config.add_setting("element_2", default="not got 2", getter=get_element_2)

        assert self.ui_element_1 == "got 1", self.ui_element_1
        assert self.ui_element_2 == "got 2", self.ui_element_2

        assert my_config.element_1 == "not got 1", my_config.element_1
        assert my_config.element_2 == "not got 2", my_config.element_2

        my_config.get(["element_1", "element_2"])

        assert my_config.element_1 == "got 1", my_config.element_1
        assert my_config.element_2 == "got 2", my_config.element_2

    def test_get__return_value_is_the_setting_value_before_the_get(self):
        my_config = nostalgic.Configuration()

        self.ui_element_1 = "got 1"
        self.ui_element_2 = "got 2"

        def get_element_1():
            return self.ui_element_1

        def get_element_2():
            return self.ui_element_2

        my_config.add_setting("element_1", default="not got 1", getter=get_element_1)
        my_config.add_setting("element_2", default="not got 2", getter=get_element_2)

        assert self.ui_element_1 == "got 1", self.ui_element_1
        assert self.ui_element_2 == "got 2", self.ui_element_2

        assert my_config.element_1 == "not got 1", my_config.element_1
        assert my_config.element_2 == "not got 2", my_config.element_2

        rv = my_config.get(["element_1", "element_2"])

        assert rv == {"element_1": "not got 1", "element_2": "not got 2"}, rv

    def test_get__settings_without_getters_dont_cause_problems(self):
        my_config = nostalgic.Configuration()

        self.ui_element_1 = "got 1"
        self.ui_element_2 = "got 2"

        def get_element_1():
            return self.ui_element_1

        def get_element_2():
            return self.ui_element_2

        my_config.add_setting("element_1", default="not got 1", getter=get_element_1)
        my_config.add_setting("element_2", default="not got 2", getter=get_element_2)
        my_config.add_setting("no_getter", default="should not have got")

        assert my_config.no_getter == "should not have got", my_config.no_getter

        rv = my_config.get(["no_getter"])

        assert rv == {}, rv

    def test_get__passing_in_nothing_calls_all_getters(self):
        my_config = nostalgic.Configuration()

        self.ui_element_1 = "got 1"
        self.ui_element_2 = "got 2"

        def get_element_1():
            return self.ui_element_1

        def get_element_2():
            return self.ui_element_2

        my_config.add_setting("element_1", default="not got 1", getter=get_element_1)
        my_config.add_setting("element_2", default="not got 2", getter=get_element_2)
        my_config.add_setting("no_getter", default="should not have got")

        my_config.get()

        assert my_config.element_1 == "got 1", my_config.element_1
        assert my_config.element_2 == "got 2", my_config.element_2

    def test_has_set(self):
        my_config = nostalgic.Configuration()

        assert hasattr(my_config, 'set')
        assert callable(my_config.set)

    def test_set__takes_list_of_settings_and_calls_their_setters(self):
        my_config = nostalgic.Configuration()

        self.element_1 = "not set 1"

        def set_element_1(value):
            self.element_1 = value

        my_config.add_setting("element_1", default="default 1", setter=set_element_1)

        assert self.element_1 == "not set 1", self.element_1
        assert my_config.element_1 == "default 1", my_config.element_1

        my_config.set(["element_1"])

        assert self.element_1 == "default 1", self.element_1
        assert my_config.element_1 == "default 1", my_config.element_1

    def test_set__calls_setters_separately(self):
        my_config = nostalgic.Configuration()

        self.element_1 = "not set 1"
        self.element_2 = "not set 2"

        def set_element_1(value):
            self.element_1 = value

        def set_element_2(value):
            self.element_2 = value

        assert self.element_1 == "not set 1", self.element_1
        assert self.element_2 == "not set 2", self.element_2

        my_config.add_setting("element_1", default="default 1", setter=set_element_1)
        my_config.add_setting("element_2", default="default 2", setter=set_element_2)

        # adding settings sets default value
        assert my_config.element_1 == "default 1", my_config.element_1
        assert my_config.element_2 == "default 2", my_config.element_2

        # adding a setting doesn't change the UI elements
        assert self.element_1 == "not set 1", self.element_1
        assert self.element_2 == "not set 2", self.element_2

        my_config.set(["element_2"])

        # calling set on element_2 doesn't affect element_1
        assert self.element_1 == "not set 1", self.element_1
        assert self.element_2 == "default 2", self.element_2

    def test_set__can_set_multiple_components_at_once(self):
        my_config = nostalgic.Configuration()

        self.element_1 = "not set 1"
        self.element_2 = "not set 2"

        def set_element_1(value):
            self.element_1 = value

        def set_element_2(value):
            self.element_2 = value

        assert self.element_1 == "not set 1", self.element_1
        assert self.element_2 == "not set 2", self.element_2

        # confirm that the configuration is still in its default state
        my_config.add_setting("element_1", default="default 1", setter=set_element_1)
        my_config.add_setting("element_2", default="default 2", setter=set_element_2)

        my_config.set(["element_1", "element_2"])

        # confirm that the elements were set
        assert self.element_1 == "default 1", self.element_1
        assert self.element_2 == "default 2", self.element_2
        assert my_config.element_1 == "default 1", my_config.element_1
        assert my_config.element_2 == "default 2", my_config.element_2

    def test_set__settings_without_setters_dont_cause_problems(self):
        my_config = nostalgic.Configuration()

        self.element_1 = "not set 1"
        self.element_2 = "not set 2"

        def set_element_1(value):
            self.element_1 = value

        def set_element_2(value):
            self.element_2 = value

        assert self.element_1 == "not set 1", self.element_1
        assert self.element_2 == "not set 2", self.element_2

        my_config.add_setting("element_1", default="default 1", setter=set_element_1)
        my_config.add_setting("element_2", default="default 2", setter=set_element_2)
        my_config.add_setting("no_setter", default="should not have been set")

        assert my_config.no_setter == "should not have been set"

        assert my_config.set(["no_setter"]) == None

    def test_set__passing_in_nothing_calls_all_setters(self):
        my_config = nostalgic.Configuration()

        self.element_1 = "not set 1"
        self.element_2 = "not set 2"

        def set_element_1(value):
            self.element_1 = value

        def set_element_2(value):
            self.element_2 = value

        assert self.element_1 == "not set 1", self.element_1
        assert self.element_2 == "not set 2", self.element_2

        my_config.add_setting("element_1", default="default 1", setter=set_element_1)
        my_config.add_setting("element_2", default="default 2", setter=set_element_2)

        my_config.set()

        assert self.element_1 == "default 1", self.element_1
        assert self.element_2 == "default 2", self.element_2


if __name__ == '__main__':
    main()
