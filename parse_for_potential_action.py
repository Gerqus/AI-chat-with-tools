from dataclasses import dataclass
from constants import AvailableActions

@dataclass
class ActionDescriptor:
    action_name: AvailableActions | None
    action_data: str | None

def parse_for_potential_action(message: str) -> ActionDescriptor:
    message_parts = message.split(" ")
    if message_parts[0] in AvailableActions and message_parts[0][0] == "[" and message_parts[0][-1] == "]":
        return ActionDescriptor(AvailableActions(message_parts[0]), message_parts[1])
    elif message_parts[0][0] == "[" and message_parts[0][-1] == "]":
        raise Exception("Unknown action: " + message_parts[0])
    else:
        return ActionDescriptor(None, None)
