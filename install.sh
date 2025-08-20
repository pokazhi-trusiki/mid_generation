#!/bin/bash

# A script to set up the Gemini MIDI Music Generator application on Manjaro/Arch-based systems.

# Define colors for output messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting the Gemini MIDI Music Generator setup...${NC}"

# --- Step 1: Verify Python and venv availability ---
echo "--> Checking for Python..."
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python is not installed. Please install Python and try again.${NC}"
    exit 1
fi

echo "--> Checking for Python's venv module..."
if ! python -c "import venv" &> /dev/null; then
    echo -e "${RED}Error: Python's 'venv' module is missing. On Arch/Manjaro, it should be included with the main python package. Please check your Python installation.${NC}"
    exit 1
fi
echo -e "${GREEN}Python and venv are available.${NC}"


# --- Step 2: Create Python Virtual Environment ---
VENV_DIR=".venv"
echo -e "\n--> Creating Python virtual environment in '${VENV_DIR}'..."
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping creation.${NC}"
else
    python -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create the virtual environment.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}Virtual environment is ready.${NC}"


# --- Step 3: Install Dependencies ---
echo -e "\n--> Activating virtual environment and installing dependencies..."
source "${VENV_DIR}/bin/activate"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install packages from requirements.txt.${NC}"
    deactivate
    exit 1
fi
deactivate
echo -e "${GREEN}All dependencies installed successfully.${NC}"


# --- Step 4: Configure API Key ---
echo -e "\n--> Setting up API key..."
if [ -f "config.ini" ]; then
    echo -e "${YELLOW}config.ini already exists. Skipping API key configuration.${NC}"
else
    echo "Please enter your Google Gemini API Key. It will not be visible as you type."
    read -s -p "Paste your API Key here: " api_key
    echo # Move to a new line

    if [ -z "$api_key" ]; then
        echo -e "${RED}Error: No API key was provided. Aborting setup.${NC}"
        exit 1
    fi

    # Create the config.ini file
    cat > config.ini << EOL
[gemini]
api_key = ${api_key}
EOL
    echo -e "${GREEN}config.ini has been created successfully.${NC}"
fi

echo -e "\n${GREEN}Step 1 of setup is complete! The application environment is now configured.${NC}"

# --- Step 5: Create the Launcher Script (run.sh) ---
echo -e "\n--> Creating the launcher script 'run.sh'..."
cat > run.sh << EOL
#!/bin/bash
# This script launches the Gemini MIDI Music Generator application.

# Navigate to the script's directory to ensure correct file paths
cd "\$(dirname "\$0")"

# Activate the virtual environment
source .venv/bin/activate

# Run the Flask application
echo "Starting the Gemini MIDI Music Generator..."
echo "Access the UI at http://127.0.0.1:5001 or http://<Your-IP-Address>:5001 in your browser."
python app.py
EOL

# Make the run.sh script executable
chmod +x run.sh

echo -e "${GREEN}Launcher script 'run.sh' created successfully.${NC}"
echo "You can now run the application anytime by executing './run.sh'."

# --- Step 6: Create Desktop Shortcut ---
echo -e "\n--> Creating desktop shortcut..."
PROJECT_DIR=$(pwd)
DESKTOP_FILE_PATH="${HOME}/Desktop/Gemini-Music-Generator.desktop"

cat > "${DESKTOP_FILE_PATH}" << EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=Gemini Music Generator
Comment=Generate MIDI music with AI
Exec="${PROJECT_DIR}/run.sh"
Icon=utilities-terminal
Terminal=true
Categories=AudioVideo;Audio;Development;
EOL

# Make the desktop file executable, which is sometimes necessary
chmod +x "${DESKTOP_FILE_PATH}"

echo -e "${GREEN}Desktop shortcut created at '${DESKTOP_FILE_PATH}'.${NC}"
echo -e "\n${GREEN}All setup steps are complete! You can now launch the application from your desktop or by running ./run.sh.${NC}"
