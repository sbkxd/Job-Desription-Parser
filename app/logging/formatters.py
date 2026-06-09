from typing import Any, Dict


def drop_color_message_key(
    logger: Any, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Ruff/Uvicorn might add a color_message. This processor drops it
    to keep structured logging output clean.
    """
    event_dict.pop("color_message", None)
    return event_dict
