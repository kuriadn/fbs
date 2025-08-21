@echo off
REM FBS Git Installation Script for Windows
REM This script installs FBS from Git source

setlocal enabledelayedexpansion

REM Set default values
set "FBS_REPO=https://github.com/fayvad/fbs.git"
set "FBS_BRANCH=main"
set "INSTALL_MODE=install"
set "PYTHON_CMD=python"
set "PIP_CMD=pip"
set "VENV_NAME=fbs-venv"
set "CREATE_VENV=false"

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :main
if "%~1"=="-r" (
    set "FBS_REPO=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--repo" (
    set "FBS_REPO=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-b" (
    set "FBS_BRANCH=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--branch" (
    set "FBS_BRANCH=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-m" (
    set "INSTALL_MODE=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--mode" (
    set "INSTALL_MODE=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-p" (
    set "PYTHON_CMD=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--python" (
    set "PYTHON_CMD=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-i" (
    set "PIP_CMD=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--pip" (
    set "PIP_CMD=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-v" (
    set "VENV_NAME=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--venv" (
    set "VENV_NAME=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-c" (
    set "CREATE_VENV=true"
    shift
    goto :parse_args
)
if "%~1"=="--create-venv" (
    set "CREATE_VENV=true"
    shift
    goto :parse_args
)
if "%~1"=="-h" (
    goto :show_usage
)
if "%~1"=="--help" (
    goto :show_usage
)
shift
goto :parse_args

:show_usage
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   -r, --repo REPO        Git repository URL (default: %FBS_REPO%)
echo   -b, --branch BRANCH    Git branch to install (default: %FBS_BRANCH%)
echo   -m, --mode MODE        Installation mode: install, editable, clone (default: %INSTALL_MODE%)
echo   -p, --python CMD       Python command (default: %PYTHON_CMD%)
echo   -i, --pip CMD          Pip command (default: %PIP_CMD%)
echo   -v, --venv NAME        Virtual environment name (default: %VENV_NAME%)
echo   -c, --create-venv      Create virtual environment
echo   -h, --help             Show this help message
echo.
echo Examples:
echo   %0                                    # Install from default repo and branch
echo   %0 -b develop                         # Install from develop branch
echo   %0 -m editable                       # Install in editable mode
echo   %0 -c -v my-venv                     # Create venv and install
echo   %0 -r https://github.com/user/fbs.git # Install from custom repo
exit /b 0

:main
echo 🚀 FBS Git Installation Script
echo ================================
echo.

call :check_prerequisites
if errorlevel 1 exit /b 1

if "%CREATE_VENV%"=="true" (
    call :create_virtual_environment
    if errorlevel 1 exit /b 1
)

call :install_fbs
if errorlevel 1 exit /b 1

call :verify_installation
if errorlevel 1 exit /b 1

call :show_next_steps
exit /b 0

:check_prerequisites
echo [INFO] Checking prerequisites...
echo.

REM Check if Python is available
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python command '%PYTHON_CMD%' not found
    exit /b 1
)

REM Check if pip is available
%PIP_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Pip command '%PIP_CMD%' not found
    exit /b 1
)

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found. Please install Git first.
    exit /b 1
)

echo [SUCCESS] Prerequisites check passed
echo.
exit /b 0

:create_virtual_environment
echo [INFO] Creating virtual environment: %VENV_NAME%
echo.

if exist "%VENV_NAME%" (
    echo [WARNING] Virtual environment '%VENV_NAME%' already exists
    set /p "REMOVE_VENV=Do you want to remove it and create a new one? (y/N): "
    if /i "!REMOVE_VENV!"=="y" (
        rmdir /s /q "%VENV_NAME%"
    ) else (
        echo [INFO] Using existing virtual environment
        goto :activate_venv
    )
)

%PYTHON_CMD% -m venv "%VENV_NAME%"
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    exit /b 1
)

echo [SUCCESS] Virtual environment created: %VENV_NAME%

:activate_venv
REM Activate virtual environment
call "%VENV_NAME%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    exit /b 1
)

echo [SUCCESS] Virtual environment activated
echo.
exit /b 0

:install_fbs
echo [INFO] Installing FBS from Git...
echo [INFO] Repository: %FBS_REPO%
echo [INFO] Branch: %FBS_BRANCH%
echo [INFO] Mode: %INSTALL_MODE%
echo.

if "%INSTALL_MODE%"=="install" (
    echo [INFO] Installing FBS in normal mode...
    %PIP_CMD% install "git+%FBS_REPO%@%FBS_BRANCH%"
) else if "%INSTALL_MODE%"=="editable" (
    echo [INFO] Installing FBS in editable mode...
    %PIP_CMD% install -e "git+%FBS_REPO%@%FBS_BRANCH%#egg=fbs-app"
) else if "%INSTALL_MODE%"=="clone" (
    echo [INFO] Cloning FBS repository...
    if exist "fbs" (
        echo [WARNING] Directory 'fbs' already exists
        set /p "REMOVE_DIR=Do you want to remove it and clone again? (y/N): "
        if /i "!REMOVE_DIR!"=="y" (
            rmdir /s /q "fbs"
        ) else (
            echo [INFO] Using existing directory
            cd fbs
            goto :install_from_clone
        )
    )
    
    git clone -b "%FBS_BRANCH%" "%FBS_REPO%" fbs
    if errorlevel 1 (
        echo [ERROR] Failed to clone repository
        exit /b 1
    )
    
    cd fbs
    echo [INFO] Installing FBS from cloned repository...
    :install_from_clone
    %PIP_CMD% install -e .
) else (
    echo [ERROR] Invalid installation mode: %INSTALL_MODE%
    exit /b 1
)

if errorlevel 1 (
    echo [ERROR] FBS installation failed
    exit /b 1
)

echo [SUCCESS] FBS installation completed
echo.
exit /b 0

:verify_installation
echo [INFO] Verifying FBS installation...
echo.

REM Test FBS import
%PYTHON_CMD% -c "import fbs_app; print('FBS imported successfully')" 2>nul
if errorlevel 1 (
    echo [ERROR] FBS import test failed
    exit /b 1
)
echo [SUCCESS] FBS import test passed

REM Test FBS interfaces import
%PYTHON_CMD% -c "from fbs_app.interfaces import FBSInterface; print('FBS interfaces imported successfully')" 2>nul
if errorlevel 1 (
    echo [ERROR] FBS interfaces import test failed
    exit /b 1
)
echo [SUCCESS] FBS interfaces import test passed

echo [SUCCESS] FBS installation verification completed
echo.
exit /b 0

:show_next_steps
echo [SUCCESS] FBS has been successfully installed!
echo.
echo Next steps:
echo 1. Add 'fbs_app.apps.FBSAppConfig' to your Django INSTALLED_APPS
echo 2. Configure your Django settings for FBS
echo 3. Run migrations: python manage.py migrate
echo 4. Create a superuser: python manage.py createsuperuser
echo.
echo For more information, see:
echo - docs/GIT_INSTALLATION.md
echo - docs/INSTALLATION_GUIDE.md
echo - README.md
echo.

if "%INSTALL_MODE%"=="clone" (
    echo You can now modify the FBS source code in the 'fbs' directory
    echo Changes will be reflected immediately due to editable installation
    echo.
)

exit /b 0
