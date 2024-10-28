
# Chat Comprehension Bot

A Python Flask-based chatbot application integrating OpenAI's ChatGPT and Amazon Polly to provide interactive conversations with comprehension feedback. The bot responds to user messages, synthesizes speech, collects user comprehension levels for each word, and provides explanations for words the user didn't fully understand.

## Features

- **Interactive Chat Interface**: Communicate with the bot using a web-based chat interface.
- **Speech Synthesis**: The bot's responses are converted to speech using Amazon Polly.
- **Word-Level Timestamps**: Each word in the bot's response includes a timestamp indicating when it is spoken in the audio.
- **Comprehension Feedback**: Users can provide comprehension levels (1-10) for each word.
- **Dynamic Explanations**: The bot provides explanations for words the user didn't fully understand.
- **Integrated Audio Playback**: Users can hear the bot's responses and explanations.

---

**Text-to-Speech Conversion**:
   - Two requests are made:
     - One for the audio stream (`mp3` format).
     - One for the speech marks (`json` format) to get word-level timestamps.

---

## Prerequisites

### Installing Python on macOS

1. **Check Existing Python Installation**:

   Open Terminal and run:

   ```bash
   python3 --version
   ```

   If Python 3.x is installed, you'll see the version number.

2. **Install Homebrew (If Not Already Installed)**:

   Homebrew is a package manager for macOS.

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. **Install Python Using Homebrew**:

   ```bash
   brew install python@3.10
   ```

   This installs Python 3.10. Adjust the version as needed.

4. **Verify Installation**:

   ```bash
   python3 --version
   ```

### Setting Up API Keys

#### OpenAI API Key

1. **Create an OpenAI Account**:

   Visit [OpenAI's website](https://platform.openai.com/signup/) and sign up for an account.

2. **Generate API Key**:

   - Go to the [API Keys page](https://platform.openai.com/account/api-keys).
   - Click on "Create new secret key".

#### Amazon AWS Access Keys

1. **Create an AWS Account**:

   Visit [AWS](https://aws.amazon.com/) and sign up for a free account.

2. **Create an IAM User**:

   - Navigate to the [IAM Console](https://console.aws.amazon.com/iam/).
   - Click on "Users" > "Add user".
   - Enter a username (e.g., `polly-user`).
   - Select "Programmatic access" for access type.
   - Click "Next: Permissions".

3. **Set Permissions**:

   - Attach existing policies directly.
   - Search for and select:
     - `AmazonPollyFullAccess`
   - Click "Next: Tags", then "Next: Review", and finally "Create user".

4. **Download Access Keys**:

   - After creating the user, you'll receive an Access Key ID and a Secret Access Key.

---

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/max-zelinski/chat-comprehension-bot.git
   cd chat-comprehension-bot
   ```

2. **Install Poetry**:

   Poetry is used for dependency management.

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   Add Poetry to your PATH as instructed after installation.

3. **Set Up the Project with Poetry**:

   ```bash
   poetry install
   ```

4. **Create a `.env` File**:

   In the project root directory, create a `.env` file to store your API keys:

   ```bash
   touch .env
   ```

   Add the following content to `.env`:

   ```ini
   OPENAI_API_KEY=your-openai-api-key
   AWS_ACCESS_KEY=your-aws-access-key-id
   AWS_SECRET_KEY=your-aws-secret-access-key
   AWS_REGION_NAME=us-west-1
   ```

---

## Running the Application

1. **Activate the Poetry Shell**:

   ```bash
   poetry shell
   ```

2. **Run the Flask Application**:

   ```bash
   python app.py
   ```

3. **Access the Application**:

   Open your web browser and navigate to:

   ```
   http://127.0.0.1:5000/
   ```

4. **Interact with the Chatbot**:

   - Type messages and interact with the assistant.
   - Adjust comprehension levels for words as needed.
   - Submit feedback to receive explanations.

---

## Project Structure

```
chat-comprehension-bot/
├── app.py
├── templates/
│   └── index.html
├── .env
├── .gitignore
├── pyproject.toml
├── poetry.lock
```

- **app.py**: The main Flask application script.
- **templates/index.html**: The HTML template for the web interface.
- **.env**: Contains environment variables (API keys).
- **pyproject.toml**: Poetry configuration file listing dependencies.

---

## Usage

1. **Sending Messages**:

   - Enter your message in the input field.
   - Click "Send" to submit.

2. **Receiving Responses**:

   - The assistant's response appears with each word followed by a timestamp.
   - The audio plays automatically.

3. **Providing Comprehension Feedback**:

   - For each word, select your comprehension level (1-10) from the dropdown.
     - **1-4**: Did not understand the word at all.
     - **5-9**: Need more clarification.
     - **10**: Understood the word completely.
   - Click "Submit Feedback".

4. **Receiving Explanations**:

   - The assistant provides explanations for words you didn't fully understand.
   - Explanations include timestamps and audio playback.