from constants import *
from utils import AdvancedAssistantManager

import time
import requests

# Firebase Setting
url = "https://project-aao-default-rtdb.firebaseio.com"
resetValue = {"condition": "Study"}


# Firebase Data Patch
response = requests.patch(f"{url}/condition.json", json=resetValue)
print(response.json())  # print to response


def main():
    manager = AdvancedAssistantManager(port_1=com_port_1, port_2=com_port_2)
    manager.set_assistant_id(assistant_id=my_assistant_id)
    manager.set_thread_id(thread_id=my_thread)

    # Get the data from Firebase
    while True:
        response = requests.get(f"{url}/condition.json")
        condition = response.json()["condition"]  # Data Approach
        time.sleep(1)  # Delay
        print("condition:", condition)

        # Condition Structure
        if condition == "Study":
            print("You are not sleeping.")
        elif condition == "Tired":
            print("You're taking the action of sleeping.")
        elif condition == "Sleep":
            message = "Set timer for 5 sec"
            print("You are sleeping!")

            # Add the message and run the assistant
            manager.add_message_to_thread(role="user", content=message)
            manager.run_assistant()

            # Wait for completions and process messages
            print("Waiting for response...")
            manager.wait_for_completion()

            # Get response from assistant and convert it to speech
            print("Converting response to speech...")
            output = manager.get_response()
            print(f"AAO: \033[95m{output}\033[0m\n")


if __name__ == "__main__":
    main()
