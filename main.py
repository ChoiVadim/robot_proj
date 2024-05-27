import io
import time
import json
import serial
import openai
import keyboard
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play

from constants import *

load_dotenv()


class AssistantManager:
    def __init__(self, model: str = "gpt-4o"):
        self.client = openai.OpenAI()
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.response = ""

    def set_assistant_id(self, assistant_id):
        self.assistant = self.client.beta.assistants.retrieve(assistant_id=assistant_id)

    def set_thread_id(self, thread_id):
        self.thread = self.client.beta.threads.retrieve(thread_id=thread_id)

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=name, instructions=instructions, tools=tools, model=self.model
            )
            self.assistant = assistant_obj
            print(f"AssisID:::: {self.assistant.id}")

        return self.assistant.id

    def create_thread(self):
        if not self.thread:
            thread_obj = self.client.beta.threads.create()
            self.thread = thread_obj
            print(f"ThreadID::: {self.thread.id}")

        return self.thread.id

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id, role=role, content=content
            )

    def run_assistant(self, instructions=""):
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions,
            )

    def process_message(self):
        if self.thread:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            last_message = messages.data[0]
            role = last_message.role
            response = last_message.content[0].text.value
            self.response = f"{role.capitalize()}: {response}"

    def get_response(self):
        return self.response

    def call_required_functions(self, required_actions):
        if not self.run:
            return
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])

            if func_name == "you function name":
                # Do something
                pass

            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Submitting outputs back to the Assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id, run_id=self.run.id, tool_outputs=tool_outputs
        )

    def wait_for_completion(self):
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id, run_id=self.run.id
                )
                # print(f"RUN STATUS:: {run_status.model_dump_json(indent=4)}")

                if run_status.status == "completed":
                    self.process_message()
                    break
                elif run_status.status == "requires_action":
                    print("FUNCTION CALLING NOW...")
                    self.call_required_functions(
                        required_actions=run_status.required_action.submit_tool_outputs.model_dump()
                    )

    def run_steps(self):
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread.id, run_id=self.run.id
        )
        print(f"Run-Steps::: {run_steps}")
        return run_steps.data


class AdvancedAssistantManager(AssistantManager):
    def __init__(self, port: str):
        super().__init__()
        self.port = port
        self.ser = self.connect_to_arduino(self.port)

    ##### Connection and Sending data to Arduino #####
    def connect_to_arduino(self, port, baud_rate=9600):
        try:
            return serial.Serial(port, baud_rate)
        except serial.SerialException as e:
            print(f"Failed to connect on {port}: {e}")

    def send_command(self, ser, command):
        try:
            ser.write(command.encode())
            print(f"Sent '{command}' to Arduino")
            return True
        except serial.SerialException as e:
            print(f"Error sending data: {e}")
            return False

    def close_connection(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Connection to {self.port} closed.")

    ##### Recording Audio, Speech to Text, and Text to Speech #####
    def record_audio(self, file_path):
        try:
            recognizer = sr.Recognizer()
            # recognizer.energy_threshold = 4000
            with sr.Microphone() as source:
                print("Please say something...")
                audio_data = recognizer.listen(source, timeout=10)
                print("Recording complete.")
                with open(file_path, "wb") as audio_file:
                    audio_file.write(audio_data.get_wav_data())
        except AttributeError:
            print("Could not find PyAudio; check installation")
            raise

    def speech_to_text(self):
        self.record_audio("audio/test.wav")
        audio_file = open("audio/test.wav", "rb")
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
        return transcription.text

    def text_to_speech(self, text):
        response = self.client.audio.speech.create(
            model="tts-1", voice="nova", input=text
        )
        byte_stream = io.BytesIO(response.content)
        audio = AudioSegment.from_file(byte_stream, format="mp3")
        play(audio)

    ##### Calling Functions #####
    def call_required_functions(self, required_actions):
        if not self.run:
            return
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])

            if func_name == "move":
                direction = arguments["direction"]
                duration = arguments["duration"]
                command = f"{direction},{duration}"
                output = self.send_command(self.ser, command)

                if output:
                    output = f"Moved {direction} for {duration} seconds"
                else:
                    output = f"Failed to move {direction} for {duration} seconds"

                tool_outputs.append(
                    {
                        "tool_call_id": action["id"],
                        "output": output,
                    }
                )

            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Submitting outputs back to the Assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id, run_id=self.run.id, tool_outputs=tool_outputs
        )


def main():
    manager = AdvancedAssistantManager(port="COM5")
    manager.set_assistant_id("asst_M8Glp6nEbIacAJUOLucT1lgy")
    manager.set_thread_id("thread_jhqGjLjSEywOV8XKhqxFPao5")

    # manager.create_assistant(
    #     name=assistant_name,
    #     instructions=instruction_for_assistant,
    #     tools=tools_for_assistant,
    # )

    # manager.create_thread()

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
            manager.text_to_speech(output)
            print(f"AAO: \033[95m{output}\033[0m\n")

        except Exception as e:
            print(f"An error occurred: {e}")
            manager.close_connection()
            break


if __name__ == "__main__":
    main()
