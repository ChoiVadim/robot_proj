from constants import *
from utils import AdvancedAssistantManager

# Set up the assistant
manager = AdvancedAssistantManager()
manager.set_assistant_id(my_assistant_id)
manager.set_thread_id(my_thread)

# Get user message
message = manager.speech_to_text()

# Add the message and run the assistant
manager.add_message_to_thread("user", message)
manager.run_assistant()

# Wait for completions and process messages
manager.wait_for_completion()

# Get response from assistant and convert it to speech
response = manager.get_response()
manager.text_to_speech(response)
