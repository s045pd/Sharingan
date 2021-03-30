import unittest

from box import Box

from sharingan import common, log


class test_normal(unittest.TestCase):
    def test_str_to_num(self):
        _ = common.str_to_num("10,11")
        self.assertEqual(_, str(1011))

    def test_status_print_1(self):
        _ = common.status_print(Box({"status_code": 101}), "101 status code")
        self.assertEqual(_, None)

    def test_status_print_2(self):
        _ = common.status_print(Box({"status_code": 201}), "201 status code")
        self.assertEqual(_, None)

    def test_status_print_3(self):
        _ = common.status_print(Box({"status_code": 304}), "304 status code")
        self.assertEqual(_, None)

    def test_status_print_4(self):
        _ = common.status_print(Box({"status_code": 401}), "401 status code")
        self.assertEqual(_, None)

    def test_status_print_5(self):
        _ = common.status_print(Box({"status_code": 502}), "502 status code")
        self.assertEqual(_, None)

    def test_status_print_unknown(self):
        _ = common.status_print(Box({"status_code": 666}), "666 status code")
        self.assertEqual(_, None)


class test_log(unittest.TestCase):
    def test_info(self):
        _ = log.info("Test log info")
        self.assertEqual(_, None)

    def test_warning(self):
        _ = log.warning("Test log warning")
        self.assertEqual(_, None)

    def test_success(self):
        _ = log.success("Test log success")
        self.assertEqual(_, None)

    def test_error(self):
        _ = log.error("Test log error")
        self.assertEqual(_, None)

    def test_critical(self):
        _ = log.critical("Test log critical")
        self.assertEqual(_, None)


class test_download(unittest.TestCase):
    def test_extract_maker(self):
        _ = common.extract_maker_with_sherlock()
        self.assertEqual(_, None)
