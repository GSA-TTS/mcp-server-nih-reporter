import logging
from importlib.resources import files

logger = logging.getLogger(__name__)

_INSTRUCTIONS_FILENAME = "server_instructions.txt"


def load_server_instructions():
    """Load the MCP server instructions text.

    Reads ``server_instructions.txt`` from this package using
    ``importlib.resources`` so the lookup is independent of the current
    working directory and works for both the source tree and an installed
    wheel.

    Returns the instructions string, or ``None`` if the file cannot be
    found. Diagnostics are sent to the logger (stderr by default) to avoid
    corrupting the stdio JSON-RPC transport.
    """
    try:
        text = (
            files("reporter.instructions")
            .joinpath(_INSTRUCTIONS_FILENAME)
            .read_text(encoding="utf-8")
        )
    except FileNotFoundError:
        logger.warning(
            "%s not found. Continuing without server instructions.",
            _INSTRUCTIONS_FILENAME,
        )
        return None

    logger.info("Server instructions loaded successfully.")
    return text
