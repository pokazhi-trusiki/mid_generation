import os
import json
import google.generativeai as genai
from flask import Flask, render_template, request, url_for, redirect

from mido import Message, MidiFile, MidiTrack, second2tick, bpm2tempo

# --- Configuration ---
# Attempt to import the API key and handle potential errors
try:
    from config import API_KEY
    genai.configure(api_key=API_KEY)
except (ImportError, FileNotFoundError, ValueError) as e:
    # If config is invalid, we can't run. We'll set a global error message.
    # The app will still run but will show an error on the main page.
    APP_ERROR = str(e)
else:
    APP_ERROR = None

# --- Constants ---
# A simple mapping for note names to MIDI numbers. C4 is middle C.
NOTE_MAP = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
    'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}
# Standard MIDI drum mapping for a few common sounds
DRUM_MAP = {
    'kick': 36, 'snare': 38, 'hi-hat': 42, 'crash': 49
}
TICKS_PER_BEAT = 480  # A standard resolution for MIDI files

# --- Flask App Initialization ---
app = Flask(__name__)
# Ensure the output directory exists
os.makedirs('static/output', exist_ok=True)

# --- Helper Functions ---

def note_name_to_midi(note_name: str) -> int:
    """Converts a note name (e.g., 'C4', 'F#5') to a MIDI pitch number."""
    if note_name[0:2].upper() in DRUM_MAP:
        return DRUM_MAP[note_name[0:2].upper()]

    note = note_name[:-1].upper()
    octave = int(note_name[-1])

    # Handle sharps
    if len(note) > 1 and note[1] == '#':
        pitch_class = NOTE_MAP[note[0:2]]
    else:
        pitch_class = NOTE_MAP[note[0]]

    return pitch_class + (octave + 1) * 12


def generate_music_data(genre: str, key: str, mood: str) -> dict | None:
    """
    Calls the Gemini API to generate musical data in a specific JSON format.
    """
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    You are an expert musician and composer. Your task is to generate a short musical composition for rock guitar and drums.
    The composition should be in the key of {key}, with a {mood} mood and in the {genre} genre.

    Please provide your output in a single JSON object, with no other text before or after it.
    The JSON object must have the following structure:
    {{
      "tempo": <integer, beats per minute, e.g., 120>,
      "tracks": [
        {{
          "instrument": "guitar",
          "notes": [
            {{"pitch": "<note name, e.g., E4>", "duration": <float, in seconds>, "velocity": <integer, 0-127>}}
          ]
        }},
        {{
          "instrument": "drums",
          "notes": [
            {{"pitch": "<drum name, e.g., kick, snare, hi-hat>", "duration": <float, in seconds>, "velocity": <integer, 0-127>}}
          ]
        }}
      ]
    }}

    Example for a guitar note: {{"pitch": "E4", "duration": 0.5, "velocity": 100}}
    Example for a drum note: {{"pitch": "kick", "duration": 0.1, "velocity": 120}}

    Keep the composition to about 4-8 bars of music. Ensure the guitar part is melodic or rhythmic and fits the specified key and mood.
    The drum part should be a corresponding beat.
    """

    try:
        response = model.generate_content(prompt)
        # Clean up the response to extract only the JSON part
        json_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(json_text)
    except Exception as e:
        print(f"Error generating music data from Gemini: {e}")
        return None


def create_midi_file(music_data: dict, filename: str) -> str:
    """
    Creates a MIDI file from the structured music data.
    Saves the file and returns its path.
    """
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    tempo = bpm2tempo(music_data.get('tempo', 120))

    for track_data in music_data['tracks']:
        track = MidiTrack()
        mid.tracks.append(track)

        # Set tempo on the first track
        if not mid.tracks[0].__dict__.get('_has_tempo'):
            track.append(Message('set_tempo', tempo=tempo, time=0))
            mid.tracks[0]._has_tempo = True

        # Set instrument (for non-drum tracks)
        # Note: MIDI channel 9 (zero-indexed) is reserved for percussion.
        is_drum_track = track_data['instrument'].lower() == 'drums'

        current_time_ticks = 0
        for note in track_data['notes']:
            duration_ticks = int(second2tick(note['duration'], TICKS_PER_BEAT, tempo))
            pitch = note_name_to_midi(note['pitch'])
            velocity = note['velocity']

            # For drums, all messages go to channel 9
            channel = 9 if is_drum_track else 0

            track.append(Message('note_on', note=pitch, velocity=velocity, time=0, channel=channel))
            track.append(Message('note_off', note=pitch, velocity=velocity, time=duration_ticks, channel=channel))

    output_path = os.path.join('static', 'output', filename)
    mid.save(output_path)
    return output_path

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main page, showing an error if the app is misconfigured."""
    if APP_ERROR:
        return render_template('index.html', error=APP_ERROR)
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """Handles the music generation request from the form."""
    if APP_ERROR:
        return redirect(url_for('index'))

    try:
        # Get form data
        genre = request.form['genre']
        key = request.form['key']
        mood = request.form['mood']
        output_filename_base = request.form['output_filename']

        # Generate music data via Gemini
        music_data = generate_music_data(genre, key, mood)
        if not music_data:
            raise Exception("Failed to generate music data from the API. The response may have been invalid.")

        # Create MIDI file
        output_filename_mid = f"{output_filename_base}.mid"
        create_midi_file(music_data, output_filename_mid)

        # Prepare download link
        download_link = url_for('static', filename=f'output/{output_filename_mid}')

        return render_template('index.html', download_link=download_link, filename=output_filename_mid)

    except Exception as e:
        print(f"An error occurred during generation: {e}")
        return render_template('index.html', error=str(e))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
