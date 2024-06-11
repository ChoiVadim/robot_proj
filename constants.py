tools_for_assistant = [
    {
        "type": "function",
        "function": {
            "name": "move",
            "description": "moving to the direction by duration",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "description": "The direction to move, e.g. 'forward' for forward, 'backward' for backward, 'left' for left, and 'right' for right",
                    },
                    "duration": {
                        "type": "integer",
                        "description": "The duration for which the robot should move, e.g. 2",
                    },
                },
                "required": ["direction", "duration"],
            },
        },
    }
]

instruction_for_assistant = "You are a robot Assistant AAO"
assistant_name = "AAO"
assistant_id = "asst_M8Glp6nEbIacAJUOLucT1lgy"
my_thread = "thread_jhqGjLjSEywOV8XKhqxFPao5"
com_port = "COM5"
