#!/bin/bash

# ANSI color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}      Automatic Lyrics Generator Installer        ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "debian"
        elif [ -f /etc/fedora-release ]; then
            echo "fedora"
        elif [ -f /etc/redhat-release ]; then
            echo "redhat"
        elif [ -f /etc/arch-release ]; then
            echo "arch"
        else
            echo "linux-other"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install ffmpeg based on OS
install_ffmpeg() {
    local os_type=$(detect_os)
    echo -e "${YELLOW}Detected OS: ${os_type}${NC}"
    
    case $os_type in
        debian)
            echo -e "${YELLOW}Installing ffmpeg using apt...${NC}"
            sudo apt-get update -y
            sudo apt-get install -y ffmpeg
            ;;
        fedora)
            echo -e "${YELLOW}Installing ffmpeg using dnf...${NC}"
            sudo dnf install -y ffmpeg
            ;;
        redhat)
            echo -e "${YELLOW}Installing ffmpeg using yum...${NC}"
            sudo yum install -y epel-release
            sudo yum install -y ffmpeg
            ;;
        arch)
            echo -e "${YELLOW}Installing ffmpeg using pacman...${NC}"
            sudo pacman -S --noconfirm ffmpeg
            ;;
        macos)
            echo -e "${YELLOW}Installing ffmpeg using Homebrew...${NC}"
            if ! command -v brew &>/dev/null; then
                echo -e "${YELLOW}Homebrew not found. Installing Homebrew...${NC}"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install ffmpeg
            ;;
        windows)
            echo -e "${YELLOW}For Windows, we'll use a Python-based ffmpeg installer...${NC}"
            pip install ffmpeg-downloader
            python -m ffmpeg_downloader.cli
            ;;
        *)
            echo -e "${RED}Unsupported OS. Please install ffmpeg manually.${NC}"
            echo -e "${YELLOW}The script will continue without ffmpeg, but some features may be limited.${NC}"
            ;;
    esac
}

# Function to install additional system dependencies
install_system_dependencies() {
    local os_type=$(detect_os)
    
    case $os_type in
        debian)
            echo -e "${YELLOW}Installing additional dependencies...${NC}"
            sudo apt-get install -y python3-dev python3-pip python3-venv portaudio19-dev
            # Install dependencies for playsound
            sudo apt-get install -y python3-gi python3-gst-1.0
            ;;
        fedora|redhat)
            echo -e "${YELLOW}Installing additional dependencies...${NC}"
            sudo dnf install -y python3-devel python3-pip python3-virtualenv portaudio-devel
            # Install dependencies for playsound
            sudo dnf install -y python3-gobject gstreamer1-plugins-base
            ;;
        arch)
            echo -e "${YELLOW}Installing additional dependencies...${NC}"
            sudo pacman -S --noconfirm python-pip python-virtualenv portaudio
            # Install dependencies for playsound
            sudo pacman -S --noconfirm python-gobject gst-plugins-base
            ;;
        macos)
            echo -e "${YELLOW}Installing additional dependencies...${NC}"
            brew install portaudio
            ;;
        windows)
            echo -e "${YELLOW}Installing additional dependencies for Windows...${NC}"
            # Windows typically doesn't need additional system packages for Python audio
            ;;
        *)
            echo -e "${YELLOW}Skipping system dependencies for unknown OS.${NC}"
            ;;
    esac
}

# Function to create command alias
create_command_alias() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local os_type=$(detect_os)
    
    # Create bin directory if it doesn't exist
    mkdir -p "$script_dir/bin"
    
    # Create the wrapper script
    cat > "$script_dir/bin/liriklagu" << EOF
#!/bin/bash
# Wrapper script for liriklagu
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="\$(dirname "\$SCRIPT_DIR")"

# Try to activate virtual environment if it exists
if [ -f "\$PARENT_DIR/venv/bin/activate" ]; then
    source "\$PARENT_DIR/venv/bin/activate"
fi

# Run the main script with either python or python3
if command -v python3 &>/dev/null; then
    python3 "\$PARENT_DIR/src/main.py" "\$@"
elif command -v python &>/dev/null; then
    python "\$PARENT_DIR/src/main.py" "\$@"
else
    echo "Error: Python is not installed. Please install Python to use this application."
    exit 1
fi
EOF
    
    # Make it executable
    chmod +x "$script_dir/bin/liriklagu"
    
    # Add to PATH based on OS
    case $os_type in
        windows)
            echo -e "${YELLOW}Creating command shortcut for Windows...${NC}"
            # Create a .bat file for Windows
            cat > "$script_dir/bin/liriklagu.bat" << EOF
@echo off
REM Wrapper script for liriklagu on Windows
setlocal

REM Get the script directory
set "SCRIPT_DIR=%~dp0"
set "PARENT_DIR=%SCRIPT_DIR%.."

REM Try to activate virtual environment if it exists
if exist "%PARENT_DIR%\venv\Scripts\activate.bat" (
    call "%PARENT_DIR%\venv\Scripts\activate.bat"
)

REM Run the main script
python "%PARENT_DIR%\src\main.py" %*

REM If python command fails, try python3
if %ERRORLEVEL% NEQ 0 (
    python3 "%PARENT_DIR%\src\main.py" %*
)

endlocal
EOF
            # Add instructions for adding to PATH
            echo -e "${YELLOW}To use the 'liriklagu' command, add the following directory to your PATH:${NC}"
            echo -e "${GREEN}$script_dir/bin${NC}"
            ;;
        *)
            # For Unix-like systems, create symlink in user's bin directory or add to .bashrc/.zshrc
            if [[ ":$PATH:" == *":$HOME/bin:"* ]]; then
                mkdir -p "$HOME/bin"
                ln -sf "$script_dir/bin/liriklagu" "$HOME/bin/liriklagu"
                echo -e "${GREEN}Command 'liriklagu' has been added to ~/bin${NC}"
            else
                # Add to .bashrc or .zshrc
                if [ -f "$HOME/.zshrc" ]; then
                    RC_FILE="$HOME/.zshrc"
                else
                    RC_FILE="$HOME/.bashrc"
                fi
                
                # Check if the path is already in the RC file
                if ! grep -q "export PATH=&quot;$script_dir/bin:\$PATH&quot;" "$RC_FILE"; then
                    echo -e "\n# Added by LirikLagu installer" >> "$RC_FILE"
                    echo "export PATH=&quot;$script_dir/bin:\$PATH&quot;" >> "$RC_FILE"
                    echo -e "${GREEN}Command 'liriklagu' has been added to your PATH in $RC_FILE${NC}"
                    echo -e "${YELLOW}Please restart your terminal or run 'source $RC_FILE' to use the command${NC}"
                fi
            fi
            ;;
    esac
}

# Check if Python is installed
echo -e "${YELLOW}Checking for Python installation...${NC}"
if command -v python3 &>/dev/null; then
    echo -e "${GREEN}Python is installed!${NC}"
    python3 --version
elif command -v python &>/dev/null; then
    echo -e "${GREEN}Python is installed!${NC}"
    python --version
else
    echo -e "${RED}Python is not installed. Installing Python...${NC}"
    
    # Install Python based on OS
    os_type=$(detect_os)
    case $os_type in
        debian)
            sudo apt-get update -y
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        fedora|redhat)
            sudo dnf install -y python3 python3-pip
            ;;
        arch)
            sudo pacman -S --noconfirm python python-pip
            ;;
        macos)
            brew install python
            ;;
        windows)
            echo -e "${RED}Please install Python from https://www.python.org/downloads/${NC}"
            echo -e "${YELLOW}The script will continue, but you'll need to install Python manually.${NC}"
            ;;
        *)
            echo -e "${RED}Unsupported OS. Please install Python manually.${NC}"
            echo -e "${YELLOW}The script will continue, but you'll need to install Python manually.${NC}"
            ;;
    esac
fi

# Check if pip is installed
echo -e "${YELLOW}Checking for pip installation...${NC}"
if command -v pip3 &>/dev/null; then
    echo -e "${GREEN}pip is installed!${NC}"
    PIP_CMD="pip3"
elif command -v pip &>/dev/null; then
    echo -e "${GREEN}pip is installed!${NC}"
    PIP_CMD="pip"
else
    echo -e "${YELLOW}pip is not installed. Trying to install pip...${NC}"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    if command -v python3 &>/dev/null; then
        python3 get-pip.py
        PIP_CMD="pip3"
    elif command -v python &>/dev/null; then
        python get-pip.py
        PIP_CMD="pip"
    else
        echo -e "${RED}Cannot install pip without Python. Please install Python first.${NC}"
        echo -e "${YELLOW}The script will continue, but some features may not work.${NC}"
        PIP_CMD=""
    fi
    rm -f get-pip.py
fi

# Check if ffmpeg is installed
echo -e "${YELLOW}Checking for ffmpeg installation...${NC}"
if command -v ffmpeg &>/dev/null; then
    echo -e "${GREEN}ffmpeg is installed!${NC}"
else
    echo -e "${YELLOW}ffmpeg is not installed. Installing ffmpeg...${NC}"
    install_ffmpeg
fi

# Install additional system dependencies
echo -e "${YELLOW}Installing additional system dependencies...${NC}"
install_system_dependencies

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Try to create virtual environment
echo -e "${YELLOW}Trying to create virtual environment...${NC}"
VENV_CREATED=false

if command -v python3 &>/dev/null; then
    python3 -m venv venv && VENV_CREATED=true || echo -e "${YELLOW}Failed to create virtual environment with python3. Continuing without it.${NC}"
elif command -v python &>/dev/null; then
    python -m venv venv && VENV_CREATED=true || echo -e "${YELLOW}Failed to create virtual environment with python. Continuing without it.${NC}"
else
    echo -e "${RED}Cannot create virtual environment without Python. Continuing without it.${NC}"
fi

# Activate virtual environment if created
if [ "$VENV_CREATED" = true ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    if source venv/bin/activate; then
        echo -e "${GREEN}Virtual environment activated successfully!${NC}"
        # Use pip from virtual environment
        PIP_CMD="pip"
    else
        echo -e "${RED}Failed to activate virtual environment. Continuing without it.${NC}"
    fi
fi

# Install packages if pip is available
if [ -n "$PIP_CMD" ]; then
    # Upgrade pip
    echo -e "${YELLOW}Upgrading pip...${NC}"
    $PIP_CMD install --upgrade pip
    
    # Install packages one by one
    echo -e "${YELLOW}Installing required packages...${NC}"
    
    # Install rich
    echo -e "${YELLOW}Installing rich...${NC}"
    $PIP_CMD install rich==13.7.0 --no-cache-dir || echo -e "${RED}Failed to install rich. Some UI features may be limited.${NC}"
    
    # Install ffmpeg-python
    echo -e "${YELLOW}Installing ffmpeg-python...${NC}"
    $PIP_CMD install ffmpeg-python==0.2.0 --no-cache-dir || echo -e "${RED}Failed to install ffmpeg-python. Audio conversion may be limited.${NC}"
    
    # Install pydub
    echo -e "${YELLOW}Installing pydub...${NC}"
    $PIP_CMD install pydub --no-cache-dir || echo -e "${RED}Failed to install pydub. Audio processing may be limited.${NC}"
    
    # Install torch (needed for whisper)
    echo -e "${YELLOW}Installing torch...${NC}"
    $PIP_CMD install torch --no-cache-dir || {
        echo -e "${YELLOW}Trying alternative torch installation...${NC}"
        $PIP_CMD install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir || echo -e "${RED}Failed to install torch. Whisper functionality may be limited.${NC}"
    }
    
    # Install numpy
    echo -e "${YELLOW}Installing numpy...${NC}"
    $PIP_CMD install numpy --no-cache-dir || echo -e "${RED}Failed to install numpy. Some features may be limited.${NC}"
    
    # Install whisper
    echo -e "${YELLOW}Installing whisper...${NC}"
    $PIP_CMD install openai-whisper --no-cache-dir || echo -e "${RED}Failed to install whisper. Transcription functionality may be limited.${NC}"
    
    # Try different playsound versions
    echo -e "${YELLOW}Installing playsound...${NC}"
    $PIP_CMD install playsound==1.2.2 --no-cache-dir || {
        echo -e "${YELLOW}Trying alternative playsound version...${NC}"
        $PIP_CMD install playsound==1.3.0 --no-cache-dir || {
            echo -e "${YELLOW}Trying PyObjC for macOS...${NC}"
            $PIP_CMD install PyObjC --no-cache-dir || {
                echo -e "${YELLOW}Trying simpleaudio as an alternative...${NC}"
                $PIP_CMD install simpleaudio --no-cache-dir || {
                    echo -e "${RED}Failed to install audio playback library. Audio playback may not work.${NC}"
                    echo -e "${YELLOW}The application will run in lyrics-only mode.${NC}"
                }
            }
        }
    }
else
    echo -e "${RED}Pip is not available. Cannot install required packages.${NC}"
    echo -e "${YELLOW}The application will run with limited functionality.${NC}"
fi

# Make the main script executable
chmod +x src/main.py

# Create command alias
echo -e "${YELLOW}Creating command alias...${NC}"
create_command_alias

echo -e "${GREEN}Installation completed successfully!${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "${YELLOW}You can now use the 'liriklagu' command to run the application${NC}"
echo -e "${YELLOW}If the command is not available, you may need to:${NC}"
echo -e "1. Restart your terminal, or"
echo -e "2. Run: ${GREEN}source ~/.bashrc${NC} or ${GREEN}source ~/.zshrc${NC}"
echo -e "3. Or run directly with: ${GREEN}./bin/liriklagu${NC}"
echo -e "${BLUE}==================================================${NC}"