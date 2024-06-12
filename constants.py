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
    },
    {
        "type": "function",
        "function": {
            "name": "set_timer",
            "description": "set the timer to some time",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration": {
                        "type": "integer",
                        "description": "The how many second timer must run",
                    },
                    "unit": {"type": "string", "enum": ["c", "f"]},
                },
                "required": ["duration"],
            },
        },
    },
]


instruction_for_assistant = "Your name is AAO. Your response must to be clean and short  as possible. Be funny.  When someone ask your name say My name is AAO. Your response must be less than 2 lines. When someone asks what are we doing today or 오늘 우리는 무엇을 하고 있나요?, say We're in 공학설계입문 전시회.  In korean, 오눌 공학설계입문 전시회 하고 있어요.Dont make your response long, make your response short and sweet. Only respond long if they ask you something in detail."
assistant_name = "AAO"
my_assistant_id = "asst_s4s0LTVgMRhzzukb0P0lP6GU"
my_thread = "thread_57R4Ub2oZ7oTkal5jY5N6Rfq"
com_port_1 = "COM5"
com_port_2 = "COM9"
