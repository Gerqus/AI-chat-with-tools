from dataclasses import dataclass
from constants import AvailableActions

@dataclass
class ActionDescriptor:
    action_name: AvailableActions | None
    action_data: str | None

def parse_for_potential_action(message: str) -> ActionDescriptor:
    message_parts = message.split(" ", maxsplit=1)
    left_bracket = message_parts[0][0]
    right_bracket = message_parts[0][-1]
    stiped_message = message_parts[0][1:-1]
    if left_bracket != "[" or right_bracket != "]":
        return ActionDescriptor(None, None)
    elif stiped_message in AvailableActions._value2member_map_:
        return ActionDescriptor(AvailableActions(stiped_message), message_parts[1])
    else:
        raise Exception("Unknown action: " + message_parts[0])
