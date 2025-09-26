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
            exit 1
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
            ;;
        fedora|redhat)
            echo -e "${YELLOW}Installing additional dependencies...${NC}"
            sudo dnf install -y python3-devel python3-pip python3-virtualenv portaudio-devel
            ;;
        arch)
            echo -e "${YELLOW}Installing additional dependencies...${NC}"
            sudo pacman -S --noconfirm python-pip python-virtualenv portaudio
            ;;
        macos)
            echo -e "${YELLOW}Installing additional dependencies...${NC}"
            brew install portaudio
            ;;
        windows)
            echo -e "${YELLOW}Installing additional dependencies for Windows...${NC}"
            # Windows typically doesn't need additional system packages for Python audio
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

# Activate virtual environment
source "\$PARENT_DIR/venv/bin/activate"

# Run the main script
python "\$PARENT_DIR/src/main.py" "\$@"
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
call "%~dp0..\venv\Scripts\activate.bat"
python "%~dp0..\src\main.py" %*
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
            exit 1
            ;;
        *)
            echo -e "${RED}Unsupported OS. Please install Python manually.${NC}"
            exit 1
            ;;
    esac
fi

# Check if pip is installed
echo -e "${YELLOW}Checking for pip installation...${NC}"
if command -v pip3 &>/dev/null; then
    echo -e "${GREEN}pip is installed!${NC}"
else
    echo -e "${YELLOW}pip is not installed. Installing pip...${NC}"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
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

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate || {
    echo -e "${RED}Failed to activate virtual environment. Please check your Python installation.${NC}"
    exit 1
}

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install packages one by one
echo -e "${YELLOW}Installing required packages...${NC}"

# Install rich
echo -e "${YELLOW}Installing rich...${NC}"
pip install rich==13.7.0 --no-cache-dir || {
    echo -e "${RED}Failed to install rich. Continuing anyway...${NC}"
}

# Install ffmpeg-python
echo -e "${YELLOW}Installing ffmpeg-python...${NC}"
pip install ffmpeg-python==0.2.0 --no-cache-dir || {
    echo -e "${RED}Failed to install ffmpeg-python. Continuing anyway...${NC}"
}

# Install pydub
echo -e "${YELLOW}Installing pydub...${NC}"
pip install pydub --no-cache-dir || {
    echo -e "${RED}Failed to install pydub. Continuing anyway...${NC}"
}

# Install torch (needed for whisper)
echo -e "${YELLOW}Installing torch...${NC}"
pip install torch --no-cache-dir || {
    echo -e "${YELLOW}Trying alternative torch installation...${NC}"
    pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir || {
        echo -e "${RED}Failed to install torch. Continuing anyway...${NC}"
    }
}

# Install numpy
echo -e "${YELLOW}Installing numpy...${NC}"
pip install numpy --no-cache-dir || {
    echo -e "${RED}Failed to install numpy. Continuing anyway...${NC}"
}

# Install whisper
echo -e "${YELLOW}Installing whisper...${NC}"
pip install openai-whisper --no-cache-dir || {
    echo -e "${RED}Failed to install whisper. Continuing anyway...${NC}"
}

# Install playsound
echo -e "${YELLOW}Installing playsound...${NC}"
pip install playsound --no-cache-dir || {
    echo -e "${RED}Failed to install playsound. Continuing anyway...${NC}"
}

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
echo -e "${BLUE}==================================================${NC}"