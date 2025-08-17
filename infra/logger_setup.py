import logging


class LoggerSetup:
    """
    A class to manage logging configuration for the project.
    """
    logging.basicConfig(
        filename="automation_log.log",
        level=logging.INFO,
        format='%(asctime)s: %(levelname)s: %(message)s',
        datefmt='%d-%m-%Y - %H:%M:%S',  # Exclude milliseconds
        force=True
    )


# Create an instance of LoggingSetup to configure logging when this module is imported
logger_setup = LoggerSetup()
