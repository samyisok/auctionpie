from django.test import TestCase

from core.errors import CodeError, GenericException


class CodeErrorTestCase(TestCase):
    def test_should_return_str_message(self):
        """ should return message """

        self.assertEqual(
            str(CodeError.UNEXPECTED_ERROR), CodeError.UNEXPECTED_ERROR.message
        )

    def test_should_return_exception_from_attr(self):
        """ should return GenericExcepton """
        exc = CodeError.UNEXPECTED_ERROR.exception

        self.assertIsInstance(exc, GenericException)
        self.assertEqual(exc.message, CodeError.UNEXPECTED_ERROR.message)
        self.assertEqual(
            exc.extensions["code"], CodeError.UNEXPECTED_ERROR.code
        )
