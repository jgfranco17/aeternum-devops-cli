from aeternum.errors import (
    AeternumBaseError,
    AeternumInputError,
    AeternumRuntimeError,
    ExitCode,
)


def test_aeternum_base_error():
    message = "Base error occurred"
    exit_code = ExitCode.RUNTIME_ERROR
    help_text = "This is a help text"
    error = AeternumBaseError(message, exit_code, help_text)
    assert error.message == message
    assert error.exit_code == exit_code
    assert error.help_text == help_text


def test_aeternum_runtime_error_default_help_text():
    message = "Runtime error occurred"
    error = AeternumRuntimeError(message)
    assert error.message == message
    assert error.exit_code == ExitCode.RUNTIME_ERROR
    assert error.help_text is not None
    assert "Help is available" in error.help_text


def test_aeternum_input_error_default_help_text():
    message = "Input error occurred"
    error = AeternumInputError(message)
    assert error.message == message
    assert error.exit_code == ExitCode.INPUT_ERROR
    assert error.help_text is not None
    assert "Help is available" in error.help_text


def test_aeternum_runtime_error_custom_help_text():
    message = "Runtime error occurred"
    help_text = "Custom help text"
    error = AeternumRuntimeError(message, help_text)
    assert error.message == message
    assert error.exit_code == ExitCode.RUNTIME_ERROR
    assert error.help_text == help_text


def test_aeternum_input_error_custom_help_text():
    message = "Input error occurred"
    help_text = "Custom help text"
    error = AeternumInputError(message, help_text)
    assert error.message == message
    assert error.exit_code == ExitCode.INPUT_ERROR
    assert error.help_text == help_text
