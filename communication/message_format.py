# communication/message_format.py
import json


def encode_message(vehicle_id, vehicle_pos, current_speed, obstacles):
    """
    Create a JSON-encoded V2V message.
    Always sends obstacles as a list (even if empty or one).
    """
    message = {
        "vehicle_id": vehicle_id,
        "vehicle_pos": vehicle_pos,
        "current_speed": current_speed,
        "obstacles": obstacles or []
    }
    return json.dumps(message).encode("utf-8")


def decode_message(data: bytes):
    """
    Decode JSON-encoded message back into Python dict.
    """
    return json.loads(data.decode("utf-8"))
