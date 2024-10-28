from flask import Flask, request, jsonify, render_template
import base64
import json
import logging
import openai
import boto3
import os
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Load API keys from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME', 'us-west-1')

# Check if API keys are set
if not OPENAI_API_KEY or not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    raise Exception("API keys are not set. Please set them as environment variables.")

# Configure OpenAI API
openai.api_key = OPENAI_API_KEY

# Configure AWS Polly client
polly_client = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION_NAME
).client('polly')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

conversation_history = [
    {
        "role": "system",
        "content": (
            "You are a helpful assistant. After each response, you will receive a list of terms "
            "the user didn't understand. Please explain these terms in simpler language. "
            "If there are no such terms, you can continue the conversation normally."
        )
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_input = data.get('user_input')
    logging.debug(f"Received user input: {user_input}")

    conversation_history.append({"role": "user", "content": user_input})

    # Get ChatGPT response
    try:
        chatgpt_response = get_chatgpt_response(conversation_history)
    except Exception as e:
        logging.error(f"Error getting response from ChatGPT: {e}")
        return jsonify({"error": "Failed to get response from ChatGPT"}), 500

    logging.debug(f"ChatGPT response: {chatgpt_response}")
    conversation_history.append({"role": "assistant", "content": chatgpt_response})

    # Convert to speech and get speech marks
    try:
        audio_base64, speech_marks = text_to_speech(chatgpt_response)
    except Exception as e:
        logging.error(f"Error converting text to speech: {e}")
        return jsonify({"error": "Failed to convert text to speech"}), 500

    logging.debug("Text-to-speech conversion successful.")

    # Map timestamps to words
    response_with_timestamps = add_timestamps_to_text(chatgpt_response, speech_marks)

    return jsonify({
        "chatgpt_response": response_with_timestamps,
        "audio_data": audio_base64,
    })

@app.route('/submit_comprehension_feedback', methods=['POST'])
def submit_comprehension_feedback():
    data = request.get_json()
    word_comprehension = data.get('word_comprehension')
    assistant_response = data.get('assistant_response')

    logging.debug(f"Received comprehension feedback: {word_comprehension}")
    logging.debug(f"Assistant response: {assistant_response}")

    # Process the comprehension feedback and get the result
    result = process_comprehension_feedback(word_comprehension, assistant_response)

    if result:
        explanation = result.get('explanation')
        audio_data = result.get('audio_data')
    else:
        explanation = None
        audio_data = None

    return jsonify({"status": "success", "explanation": explanation, "audio_data": audio_data})

def process_comprehension_feedback(word_comprehension, assistant_response):
    # Convert comprehension values to integers
    try:
        word_comprehension = [int(c) for c in word_comprehension]
    except ValueError as e:
        logging.error(f"Error converting comprehension values to int: {e}")
        return None

    # Remove timestamps from assistant_response
    words_with_timestamps = assistant_response.split()
    words = []
    for item in words_with_timestamps:
        match = re.match(r'(.+)\[\d+ms\]', item)
        if match:
            words.append(match.group(1))
        else:
            words.append(item)

    # Log the comprehension values and assistant response
    logging.debug(f"Word comprehension (converted to int): {word_comprehension}")
    logging.debug(f"Assistant response words: {words}")

    # Check if lengths match
    if len(word_comprehension) != len(words):
        logging.error("Mismatch between number of words and comprehension values.")
        return None

    # Identify words that the user did not fully understand (comprehension less than 10)
    problematic_words = [words[i] for i, comprehension in enumerate(word_comprehension) if comprehension < 10]

    if problematic_words:
        # Create a message to inform ChatGPT about the problematic words
        feedback_message_content = f"The user did not fully understand the following terms: {', '.join(problematic_words)}. Please explain these terms."

        logging.debug(f"Sending feedback to ChatGPT: {feedback_message_content}")

        # Append the feedback message to the conversation history as a user message
        conversation_history.append({"role": "user", "content": feedback_message_content})

        # Get ChatGPT's explanation
        try:
            explanation_response = get_chatgpt_response(conversation_history)
        except Exception as e:
            logging.error(f"Error getting explanation from ChatGPT: {e}")
            return None

        logging.debug(f"ChatGPT's explanation: {explanation_response}")

        # Append ChatGPT's explanation to the conversation history
        conversation_history.append({"role": "assistant", "content": explanation_response})

        # Generate audio and speech marks for the explanation
        try:
            audio_base64, speech_marks = text_to_speech(explanation_response)
        except Exception as e:
            logging.error(f"Error converting explanation to speech: {e}")
            audio_base64 = None
            speech_marks = []

        # Map timestamps to words in the explanation
        explanation_with_timestamps = add_timestamps_to_text(explanation_response, speech_marks)

        # Return the explanation with timestamps and audio data
        return {
            "explanation": explanation_with_timestamps,
            "audio_data": audio_base64
        }

    else:
        logging.debug("No problematic words identified.")
        return None

def get_chatgpt_response(conversation):
    logging.debug(f"Sending messages to OpenAI API: {conversation}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=150
    )
    logging.debug(f"Received response from OpenAI API: {response}")

    if response.choices:
        assistant_message = response.choices[0].message['content']
        logging.debug(f"Assistant's response: {assistant_message}")
        return assistant_message
    else:
        raise Exception("No response from ChatGPT")

def text_to_speech(text):
    import re
    logging.debug(f"Converting text to speech: {text}")

    # First, get the audio stream
    try:
        response_audio = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'
        )
        audio_stream = response_audio.get('AudioStream')
        audio_data = audio_stream.read() if audio_stream else None
    except Exception as e:
        logging.error(f"Error retrieving audio from Polly: {e}")
        audio_data = None

    # Then, get the speech marks
    try:
        response_marks = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='json',
            VoiceId='Joanna',
            SpeechMarkTypes=['word']
        )
        speech_marks_stream = response_marks.get('AudioStream')
        speech_marks = []
        if speech_marks_stream:
            speech_marks_data = speech_marks_stream.read().decode('utf-8')
            for line in speech_marks_data.strip().split('\n'):
                mark = json.loads(line)
                if mark['type'] == 'word':
                    speech_marks.append(mark)
    except Exception as e:
        logging.error(f"Error retrieving speech marks from Polly: {e}")
        speech_marks = []

    # Encode the audio stream to base64
    if audio_data:
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    else:
        audio_base64 = None
        logging.error("No audio stream returned from Polly.")

    logging.debug("Audio stream and speech marks received and processed.")

    return audio_base64, speech_marks

def add_timestamps_to_text(text, speech_marks):
    words = text.split()
    response_with_timestamps = ''
    for i, word in enumerate(words):
        if i < len(speech_marks):
            timestamp = speech_marks[i]['time']
            response_with_timestamps += f"{word}[{timestamp}ms] "
        else:
            response_with_timestamps += f"{word} "
    return response_with_timestamps.strip()

if __name__ == '__main__':
    app.run(debug=True)
