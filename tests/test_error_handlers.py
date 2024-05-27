"""
Test cases for Error Handlers
"""


import unittest
from service.common.error_handlers import bad_request, not_found, method_not_supported


class TestErrorHandlers(unittest.TestCase):
    """Error Handlers testcase """
    def test_bad_request(self):
        """ bad request test """
        bad_errror = bad_request("error")

        self.assertIsInstance(bad_errror, tuple)

    def test_not_found(self):
        """ not_found test """
        bad_errror = not_found("error")

        self.assertIsInstance(bad_errror, tuple)

    def test_method_not_supported(self):
        """ method_not_supported  test """
        bad_errror = method_not_supported("error")

        self.assertIsInstance(bad_errror, tuple)
