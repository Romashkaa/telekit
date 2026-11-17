import telekit

loaded: list[str] = telekit.utils.load_modules(__name__)

telekit._logger.library_logger.info(
    f"Welcome to the Telekit family!\n\n"
    f"Loaded {len(loaded)} example handlers:\n"
    f"{'\n'.join(loaded)}\n"
)
