@echo off

REM Create a virtual environment
python -m venv .venv

REM Activate the virtual environment
call .venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Exit with success message
echo Virtual environment created and dependencies installed successfully.
