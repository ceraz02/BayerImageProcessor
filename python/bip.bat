@echo off
REM Activate the virtual environment
CALL C:\path to BayerImageProcessor\.venv\Scripts\activate.bat

REM Call the Python script with all arguments
python C:\path to BayerImageProcessor\python\BayerImageProcessor.py %*
