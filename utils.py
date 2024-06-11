import io
import time
import json
import serial
import openai
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
    def __init__(self, port_1: str, port_2: str):
        super().__init__()
        self.port_1 = port_1
        self.port_2 = port_2
        self.ser_1 = self.connect_to_arduino(self.port_1)
        self.ser_2 = self.connect_to_arduino(self.port_2)

    ##### Connection and Sending data to Arduino #####
    def connect_to_arduino(self, port, baud_rate=9600):
        try:
            return serial.Serial(port, baud_rate)
        except serial.SerialException as e:
            print(f"Failed to connect on {port}: {e}")

    def send_command(self, ser, command):
        try:
            if not ser:
                return False
            ser.write(command.encode())
            print(f"Sent '{command}' to Arduino")
            return True

        except serial.SerialException as e:
            print(f"Error sending data: {e}")
            return False

    def receive_message_from_arduino(self, ser, port):
        try:
            message = ser.readline().decode().strip()
            print(f"Received message from Arduino on port {port}: {message}")
            return message
        except serial.SerialException as e:
            print(f"Error receiving message from Arduino on port {port}: {e}")
            return None

    def close_connection(self):
        if self.ser_1 and self.ser_1.is_open:
            self.ser_1.close()
            print(f"Connection to {self.port_1} closed.")

        if self.ser_2 and self.ser_2.is_open:
            self.ser_2.close()
            print(f"Connection to {self.port_2} closed.")

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
                output = self.send_command(self.ser_1, command)

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

            elif func_name == "set_timer":
                duration = arguments["duration"]
                command = f"timer, {duration}"
                output = self.send_command(self.ser_2, command)
                msg = self.receive_message_from_arduino(
                    ser=self.ser_2, port=self.port_2
                )
                if msg:
                    self.text_to_speech(f"Wake up brooooh!")
                    self.send_command(self.ser_1, "wakeup,1")

                if output:
                    output = f"Set timer for {duration} seconds"
                else:
                    output = f"Failed to set timer for {duration} seconds"

                tool_outputs.append(
                    {
                        "tool_call_id": action["id"],
                        "output": output,
                    }
                )

            else:
                print(f"Unknown function: {func_name}")

        print("Submitting outputs back to the Assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id, run_id=self.run.id, tool_outputs=tool_outputs
        )


def main():
    manager = AssistantManager()
    manager.create_assistant(
        name=assistant_name,
        instructions=instruction_for_assistant,
        tools=tools_for_assistant,
    )

    manager.create_thread()


if __name__ == "__main__":
    main()
