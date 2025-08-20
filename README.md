# Gemini MIDI Music Generator

This project is a web-based application that uses Google's Gemini API to generate short, two-track (guitar and drums) musical compositions in MIDI format based on user-defined parameters.

## Features

- **Web-based UI:** Easy-to-use interface accessible from any browser on your local network (PC or mobile).
- **Customizable Generation:** Specify the genre, key, and mood for your composition.
- **AI-Powered:** Leverages the Gemini API to create unique musical ideas.
- **MIDI Output:** Generates standard `.mid` files that can be downloaded and used in any Digital Audio Workstation (DAW) or MIDI player.

## Requirements

- Python 3.7+
- A modern web browser (e.g., Chrome, Firefox, Safari)
- A Google Gemini API Key

## Installation

1.  **Get the Code:**
    Clone this repository or download the source code files to a directory on your computer.

2.  **Set Up Configuration:**
    - In the project directory, find the `config.ini.template` file.
    - Make a copy of this file and rename it to `config.ini`.
    - Open `config.ini` with a text editor and replace `YOUR_API_KEY_HERE` with your actual Google Gemini API key.

    ```ini
    [gemini]
    api_key = sk-YourActualKeyGoesHere...
    ```

3.  **Install Dependencies:**
    - Open a terminal or command prompt in the project directory.
    - It's recommended to use a Python virtual environment.
    - Install the required libraries by running:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the Application:**
    - In your terminal, from the project directory, run the following command:
    ```bash
    python app.py
    ```
    - You should see output indicating that a Flask server is running, similar to this:
    ```
     * Running on http://127.0.0.1:5001
     * Running on http://Your.Computers.IP.Address:5001
    ```

2.  **Access from your PC:**
    - Open your web browser and navigate to `http://127.0.0.1:5001`.

3.  **Access from your Phone (Optional):**
    - Make sure your phone is connected to the **same Wi-Fi network** as your computer.
    - Find your computer's local IP address. (On Windows, use `ipconfig` in the command prompt. On macOS/Linux, use `ifconfig` or `ip addr`).
    - Open the browser on your phone and navigate to `http://<Your-Computer-IP-Address>:5001` (e.g., `http://192.168.1.15:5001`).

4.  **Generate Music:**
    - Fill in the fields in the web form (or use the defaults).
    - Click the "Сгенерировать музыку" (Generate Music) button.
    - After a few moments, a download link for your MIDI file will appear on the page.

## How It Works

The application uses a Flask web server to provide the UI. When you submit the form, the server constructs a detailed prompt based on your input and sends it to the Gemini API. Gemini returns a structured JSON object describing the notes of the composition. The Flask server then parses this JSON and uses the `mido` library to build a standard MIDI file, which is saved to the `static/output` directory and made available for you to download.
