import os
import time
import tempfile
import traceback

import nostalgic


def post_test_clean_up():
    """Run after each test."""
    # clear singleton so that runs are separate
    nostalgic.Configuration._SingletonMetaclass__reset()


class TestConfiguration:

    def test_instance_type(self):
        my_settings = nostalgic.Configuration()
        assert isinstance(my_settings, object)

    def test_add_setting(self):
        my_settings = nostalgic.Configuration()

        my_settings.add_setting("path", initial="/my/path")
        assert hasattr(my_settings, "path")

    def test_initial(self):
        my_settings = nostalgic.Configuration()

        my_settings.add_setting("path", initial="/my/path")
        assert my_settings.path == "/my/path"

    def test_set_attr(self):
        my_settings = nostalgic.Configuration()

        try:
            my_settings.banana = "Rama"
        except AttributeError:
            pass
        else:
            raise AssertionError("Did not throw an AttributeError!")

        my_settings.add_setting("banana", initial="Rama")
        assert my_settings.banana == "Rama"

    def test_get_attr(self):
        my_settings = nostalgic.Configuration()

        try:
            assert my_settings.banana is not None
        except AttributeError:
            pass
        else:
            raise AssertionError("Did not throw an AttributeError!")

        my_settings.add_setting("banana", initial="Rama")
        assert my_settings.banana == "Rama"

    def test_singleton(self):
        my_settings = nostalgic.Configuration()
        my_other_settings = nostalgic.Configuration()

        assert my_settings == my_other_settings

    def test_dict_getter(self):
        my_settings = nostalgic.Configuration()

        try:
            my_settings['Rama'] == 'banana'
        except KeyError:
            pass
        else:
            raise AssertionError("Should throw KeyError")

        my_settings.add_setting("banana", initial="Rama")
        assert my_settings['banana'] == 'Rama'

    def test_dict_setter(self):
        my_settings = nostalgic.Configuration()

        try:
            my_settings['banana'] = 'fail'
        except KeyError:
            pass
        else:
            raise AssertionError

        my_settings.add_setting("banana")
        my_settings['banana'] = "Rama"

        assert my_settings['banana'] == 'Rama'

    def test_whether_a_setting_exists(self):
        my_settings = nostalgic.Configuration()

        my_settings.add_setting('banana')
        assert 'banana' in my_settings

    def test_number_of_settings(self):
        my_settings = nostalgic.Configuration()

        assert len(my_settings) == 0

        my_settings.add_setting('banana')
        assert len(my_settings) == 1

        my_settings.add_setting('Rama')
        assert len(my_settings) == 2

    def test_getter(self):
        my_settings = nostalgic.Configuration()

        fake_ui_element = 100
        def get_from_fake_ui_element():
            return fake_ui_element

        my_settings.add_setting("my_setting", getter=get_from_fake_ui_element, initial=42)
        assert hasattr(my_settings, "my_setting")

        assert my_settings._proxy['my_setting']['getter'] == get_from_fake_ui_element

        assert my_settings._proxy['my_setting']['getter']() == 100

        fake_ui_element = 25
        assert my_settings._proxy['my_setting']['getter']() == 25

    def test_setter(self):
        my_settings = nostalgic.Configuration()

        self.fake_ui_element = 100

        def set_fake_ui_element(value):
            self.fake_ui_element = value

        my_settings.add_setting("my_setting", setter=set_fake_ui_element, initial=42)
        assert hasattr(my_settings, "my_setting")

        assert my_settings._proxy['my_setting']['setter'] == set_fake_ui_element

        assert self.fake_ui_element == 100
        my_settings._proxy['my_setting']['setter'](25)
        assert self.fake_ui_element == 25

    def test_default_save_location(self):
        my_settings = nostalgic.Configuration()
        assert my_settings._filename == os.path.expanduser('~')

    def test_custom_save_location(self):
        with tempfile.TemporaryFile() as temp_file:
            my_settings = nostalgic.Configuration(temp_file)

        assert my_settings._filename == temp_file

    # def test_write(self):
    #     with tempfile.TemporaryFile() as temp_file:
    #         my_settings = nostalgic.Configuration(temp_file)

    #         my_settings.add_setting("first", initial=1)
    #         my_settings.add_setting("second", initial=2)
    #         my_settings.add_setting("write", initial="wrong")
    #         my_settings.write_()

    #         with open(temp_file, 'r', encoding='utf-8') as f:
    #             ini = f.read()

    #     assert ini == "[General]\nfirst=1\nsecond=2\nwrite=wrong"

    # TODO implement syncing


if __name__ == '__main__':

    test_suite     = TestConfiguration()
    test_functions = [getattr(test_suite, m)
                     for m in dir(test_suite)
                     if m[:4] == 'test']

    tests_to_run = [
        *test_functions,
        # test_suite.test_get_attr
    ]
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
            print(f"  [FAIL]: {ex}", flush=True)
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
