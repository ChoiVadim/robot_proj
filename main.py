import keyboard

from constants import *
from utils import AdvancedAssistantManager


def main():
    manager = AdvancedAssistantManager(
        port_1=com_port_1,
    )
    manager.set_assistant_id(assistant_id=my_assistant_id)
    manager.set_thread_id(thread_id=my_thread)

    while True:
        print("Press 'spacebar' to start the while loop...")
        keyboard.wait("space")

        try:
            # Get user input
            input = manager.speech_to_text()
            print(f"Human: \033[94m{input}\033[0m\n")

            if not input:
                continue

            # Add the message and run the assistant
            manager.add_message_to_thread(role="user", content=input)
            manager.run_assistant()

            # Wait for completions and process messages
            print("Waiting for response...")
            manager.wait_for_completion()

            # Get response from assistant and convert it to speech
            print("Converting response to speech...")
            output = manager.get_response()
            print(f"AAO: \033[95m{output}\033[0m\n")
            manager.text_to_speech(output)

        except KeyboardInterrupt:
            print("KeyboardInterrupt: Exiting program...")
            manager.close_connection()

        except Exception as e:
            print(f"An error occurred: {e}")
            break


if __name__ == "__main__":
    main()
