#!/bin/bash

# FBS Git Installation Script
# This script installs FBS from Git source

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
FBS_REPO="https://github.com/fayvad/fbs.git"
FBS_BRANCH="main"
INSTALL_MODE="install"  # install, editable, or clone
PYTHON_CMD="python3"
PIP_CMD="pip3"
VENV_NAME="fbs-venv"
CREATE_VENV=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -r, --repo REPO        Git repository URL (default: $FBS_REPO)"
    echo "  -b, --branch BRANCH    Git branch to install (default: $FBS_BRANCH)"
    echo "  -m, --mode MODE        Installation mode: install, editable, clone (default: $INSTALL_MODE)"
    echo "  -p, --python CMD       Python command (default: $PYTHON_CMD)"
    echo "  -i, --pip CMD          Pip command (default: $PIP_CMD)"
    echo "  -v, --venv NAME        Virtual environment name (default: $VENV_NAME)"
    echo "  -c, --create-venv      Create virtual environment"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Install from default repo and branch"
    echo "  $0 -b develop                         # Install from develop branch"
    echo "  $0 -m editable                       # Install in editable mode"
    echo "  $0 -c -v my-venv                     # Create venv and install"
    echo "  $0 -r https://github.com/user/fbs.git # Install from custom repo"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Python is available
    if ! command -v $PYTHON_CMD &> /dev/null; then
        print_error "Python command '$PYTHON_CMD' not found"
        exit 1
    fi
    
    # Check if pip is available
    if ! command -v $PIP_CMD &> /dev/null; then
        print_error "Pip command '$PIP_CMD' not found"
        exit 1
    fi
    
    # Check if git is available
    if ! command -v git &> /dev/null; then
        print_error "Git not found. Please install Git first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create virtual environment
create_virtual_environment() {
    if [ "$CREATE_VENV" = true ]; then
        print_status "Creating virtual environment: $VENV_NAME"
        
        if [ -d "$VENV_NAME" ]; then
            print_warning "Virtual environment '$VENV_NAME' already exists"
            read -p "Do you want to remove it and create a new one? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -rf "$VENV_NAME"
            else
                print_status "Using existing virtual environment"
                return
            fi
        fi
        
        $PYTHON_CMD -m venv "$VENV_NAME"
        print_success "Virtual environment created: $VENV_NAME"
        
        # Activate virtual environment
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            source "$VENV_NAME/Scripts/activate"
        else
            source "$VENV_NAME/bin/activate"
        fi
        
        print_success "Virtual environment activated"
    fi
}

# Function to install FBS
install_fbs() {
    print_status "Installing FBS from Git..."
    print_status "Repository: $FBS_REPO"
    print_status "Branch: $FBS_BRANCH"
    print_status "Mode: $INSTALL_MODE"
    
    case $INSTALL_MODE in
        "install")
            print_status "Installing FBS in normal mode..."
            $PIP_CMD install "git+$FBS_REPO@$FBS_BRANCH"
            ;;
        "editable")
            print_status "Installing FBS in editable mode..."
            $PIP_CMD install -e "git+$FBS_REPO@$FBS_BRANCH#egg=fbs-app"
            ;;
        "clone")
            print_status "Cloning FBS repository..."
            if [ -d "fbs" ]; then
                print_warning "Directory 'fbs' already exists"
                read -p "Do you want to remove it and clone again? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm -rf "fbs"
                else
                    print_status "Using existing directory"
                    cd fbs
                    return
                fi
            fi
            
            git clone -b "$FBS_BRANCH" "$FBS_REPO" fbs
            cd fbs
            print_status "Installing FBS from cloned repository..."
            $PIP_CMD install -e .
            ;;
        *)
            print_error "Invalid installation mode: $INSTALL_MODE"
            exit 1
            ;;
    esac
    
    print_success "FBS installation completed"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying FBS installation..."
    
    if $PYTHON_CMD -c "import fbs_app; print('FBS imported successfully')" 2>/dev/null; then
        print_success "FBS import test passed"
    else
        print_error "FBS import test failed"
        exit 1
    fi
    
    if $PYTHON_CMD -c "from fbs_app.interfaces import FBSInterface; print('FBS interfaces imported successfully')" 2>/dev/null; then
        print_success "FBS interfaces import test passed"
    else
        print_error "FBS interfaces import test failed"
        exit 1
    fi
    
    print_success "FBS installation verification completed"
}

# Function to show next steps
show_next_steps() {
    print_success "FBS has been successfully installed!"
    echo ""
    echo "Next steps:"
    echo "1. Add 'fbs_app.apps.FBSAppConfig' to your Django INSTALLED_APPS"
    echo "2. Configure your Django settings for FBS"
    echo "3. Run migrations: python manage.py migrate"
    echo "4. Create a superuser: python manage.py createsuperuser"
    echo ""
    echo "For more information, see:"
    echo "- docs/GIT_INSTALLATION.md"
    echo "- docs/INSTALLATION_GUIDE.md"
    echo "- README.md"
    echo ""
    
    if [ "$INSTALL_MODE" = "clone" ]; then
        echo "You can now modify the FBS source code in the 'fbs' directory"
        echo "Changes will be reflected immediately due to editable installation"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--repo)
            FBS_REPO="$2"
            shift 2
            ;;
        -b|--branch)
            FBS_BRANCH="$2"
            shift 2
            ;;
        -m|--mode)
            INSTALL_MODE="$2"
            shift 2
            ;;
        -p|--python)
            PYTHON_CMD="$2"
            shift 2
            ;;
        -i|--pip)
            PIP_CMD="$2"
            shift 2
            ;;
        -v|--venv)
            VENV_NAME="$2"
            shift 2
            ;;
        -c|--create-venv)
            CREATE_VENV=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo "🚀 FBS Git Installation Script"
    echo "================================"
    echo ""
    
    check_prerequisites
    create_virtual_environment
    install_fbs
    verify_installation
    show_next_steps
}

# Run main function
main "$@"
