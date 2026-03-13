
import logging
import time

from tests.androidtv.pages.utility.stbconfig import STBConfig

NOTE_LEVEL = 25
logging.addLevelName(NOTE_LEVEL, "NOTE")


class EnhancedLogger(logging.Logger):
    """
    Enhanced Logger class with custom NOTE level support.
    Provides proper IDE support for the note method.
    """
    
    def note(self, message, *args, **kwargs):
        """
        Log a message with severity 'NOTE'.
        
        Args:
            message: The log message
            *args: Arguments for string formatting
            **kwargs: Keyword arguments for logging
        """
        if self.isEnabledFor(NOTE_LEVEL):
            self._log(NOTE_LEVEL, message, args, **kwargs)


# Set the custom logger class as the default
logging.setLoggerClass(EnhancedLogger)


class ColoredFormatter(logging.Formatter):
    COLOR_CODES = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[1;91m",  # Bold Red
        "NOTE": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLOR_CODES.get(record.levelname, self.RESET)
        record.msg = f"{log_color}{record.msg}{self.RESET}"
        return super().format(record)


class Logger:

    def __init__(self):
        self.step_counter = 1  # Initialize the step counter

    def create_stream_handler(self, formatter):
        """Creates and returns a stream handler with the given formatter."""
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        return handler

    def setup_logger(self, logger_name, level=logging.DEBUG) -> EnhancedLogger:
        """Sets up and returns an enhanced logger with colored output and custom note method."""
        logger = logging.getLogger(logger_name)
        logger.propagate = (
            False  # Prevent log messages from propagating to the root logger
        )
        if logger.hasHandlers():
            logger.handlers.clear()  # Clear existing handlers to avoid duplicates
        formatter = ColoredFormatter("%(levelname)s: %(name)s: %(message)s")
        handler = self.create_stream_handler(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        return logger  # type: ignore[return-value]

    def print_indented_line_with_delay(self, n, line: int):
        """Prints a line of 80 hyphens, indented to the fifth column, with a delay of n seconds before and after printing the line, line times.

        Args:
            n (int): The number of seconds to delay before and after printing the line.
            line (int): The number of lines to print.
        """
        time.sleep(n)
        for _ in range(line):
            print(
                " - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
            )
        time.sleep(n)

    def print_separator_with_delay(self, n, line: int):
        """
        Prints a separator line of hyphens with a delay before and after printing.

        Args:
            n (int): The number of seconds to delay before and after printing the separator line.
            line (int): The number of separator lines to print.
        """

        time.sleep(n)
        for _ in range(line):
            print(
                "------------------------------------------------------------------------------------"
            )

        time.sleep(n)

    def step_action(self, statement):
        """
        Logs a step action statement with an incremented step counter.

        This method sets up a logger with the specified name and logs a step
        action message, formatted in bold, using the current step counter.
        After logging, the step counter is incremented.

        Args:
            log_name (str): The name of the logger to set up.
            statement (str): The step action statement to log.
        """

        log = self.setup_logger(STBConfig.test_id)
        print("")
        log.info(
            "\033[1mSTEP ACTION %s: %s\033[0m", self.step_counter, statement
        )  # Bold (statement)
        self.step_counter += 1  # Increment the step counter

    def expected_result(self, statement):
        """
        Logs an expected result statement with a delay before and after printing.

        This method sets up a logger with the specified name and logs an expected
        result message, formatted in bold, using the specified statement.
        After logging, a line of 80 hyphens is printed with a delay of 1 second.

        Args:
            log_name (str): The name of the logger to set up.
            statement (str): The expected result statement to log.
        """
        log = self.setup_logger(STBConfig.test_id)
        log.info("\033[1mEXPECTED RESULT: %s\033[0m", statement)  # Bold (statement)
        self.print_indented_line_with_delay(1, 1)

    def action_result(self, statement):
        """
        Logs an action result statement with a delay before and after printing.

        This method sets up a logger with the specified name and logs an action
        result message, formatted in bold, using the specified statement.
        Before logging, a line of 80 hyphens is printed with a delay of 1 second.
        After logging, another line of 80 hyphens is printed with a delay of 1 second.

        Args:
            log_name (str): The name of the logger to set up.
            statement (str): The action result statement to log.
        """
        log = self.setup_logger(STBConfig.test_id)
        self.print_indented_line_with_delay(1, 1)
        log.info("\033[1mSTEP ACTION RESULT: %s\033[0m", statement)  # Bold (statement)
        self.print_separator_with_delay(1, 2)

    def print_statement_with_bold(self, statement):
        """
        Logs a statement with bold formatting.

        This method sets up a logger with the specified name and logs a statement
        formatted in bold.

        Args:
            log_name (str): The name of the logger to set up.
            statement (str): The statement to log with bold formatting.
        """
        log = self.setup_logger(STBConfig.test_id)
        log.info("\033[1m%s\033[0m", statement)  # Bold (statement)

    def print_separator(self):
        """
        Prints a separator line of hyphens to visually separate test cases.

        A 2 second delay is introduced before and after printing the separator line.
        """
        time.sleep(2)
        print(
            "==================================================================================="
        )

    def log_test_success(self):
        """
        Logs a success message to indicate that the test case has been executed successfully.

        This method prints a separator line of hyphens, followed by a success message
        formatted in bold, and finally another separator line of hyphens.
        """

        self.print_separator()
        self.print_statement_with_bold("RESULT : Test case executed successfully!!")
        self.print_separator()

    def log_test_case_info(self, message):
        """
        Logs test case information with bold formatting.

        This method is a generic function for logging test case details like test completion,
        test case name, or any other test case related information. It automatically uses
        the test_id from STBConfig internally, so you don't need to pass it explicitly.

        Args:
            message (str): The test case information message to log.
        """
        log = self.setup_logger(STBConfig.test_id)
        log.info("\033[1m%s\033[0m", message)  # Bold (message)

    def log_test_case_warning(self, message):
        """
        Logs test case warning information with bold formatting.

        This method is a generic function for logging test case warning details.
        It automatically uses the test_id from STBConfig internally, so you don't need to pass it explicitly.

        Args:
            message (str): The test case warning message to log.
        """
        log = self.setup_logger(STBConfig.test_id)
        log.warning("\033[1m%s\033[0m", message)  # Bold (message)

    def log_test_case_debug(self, message):
        """
        Logs test case debug information with bold formatting.

        This method is a generic function for logging test case debug details.
        It automatically uses the test_id from STBConfig internally, so you don't need to pass it explicitly.

        Args:
            message (str): The test case debug message to log.
        """
        log = self.setup_logger(STBConfig.test_id)
        log.debug("\033[1m%s\033[0m", message)  # Bold (message)

    def log_test_case_error(self, message):
        """
        Logs test case error information with bold formatting.

        This method is a generic function for logging test case error details.
        It automatically uses the test_id from STBConfig internally, so you don't need to pass it explicitly.

        Args:
            message (str): The test case error message to log.
        """
        log = self.setup_logger(STBConfig.test_id)
        log.error("\033[1m%s\033[0m", message)  # Bold (message)

    def log_test_case_note(self, message):
        """
        Logs test case NOTE information (bold) using the custom NOTE level.
        """
        log = self.setup_logger(STBConfig.test_id)
        log.note("🔵 \033[1;4m%s\033[0m", message)


def test_colored_logger():
    """
    Tests the colored logger.
    """
    logger = Logger()
    log = logger.setup_logger("TestLogger")

    log.debug("This is a debug message.")
    log.info("This is an info message.")
    log.warning("This is a warning message.")
    log.error("This is an error message.")
    log.note("This is a note message.")
    logger.log_test_case_note("This is a test case note message.")
