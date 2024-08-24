# README

This README provides an overview of the OCR project and guides you through the setup process.

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Files](#files)
- [Usage](#usage)
- [Contributing](#contributing)

## Introduction
The TesseractOCR project utilizes Tesseract, an open-source OCR engine, to extract text from images. This README will guide you through the setup process and provide information on the project files.

## Installation
To get started with the OCR project, follow these steps:

1. Create a virtual environment using `venv`:
    ```
    python -m venv ocr-env
    ```

2. Activate the virtual environment:
    - For Windows:
      ```
      ocr-env\Scripts\activate
      ```
    - For macOS/Linux:
      ```
      source ocr-env/bin/activate
      ```

3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Install Tesseract locally:
    - For Windows, download the installer from the [Tesseract GitHub page](https://github.com/UB-Mannheim/tesseract/wiki) and follow the installation instructions.
    - For macOS, use Homebrew:
      ```
      brew install tesseract
      ```
    - For Linux, use your package manager:
      ```
      sudo apt-get install tesseract-ocr
      ```

5. Build the executable using PyInstaller:
    ```
    pyinstaller --onefile --add-data "C:\Program Files\Tesseract-OCR;tesseract" --add-data "venv\Lib\site-packages\tkinterdnd2;tkinterdnd2" --add-data "venv\Lib\site-packages\tkinterdnd2\tkdnd;tkdnd" --hidden-import tkinterdnd2 main.py 
    ```

## Files
This section provides information on the three main files in the project:

1. `main.py`: This file contains the main code for the OCR project, Using tkinter module the gui is created for the ease of the user.

2. `old_main.py`: This file contains the code without the gui.

3. `bot_main.py`: This file contains the code for the implementation of bot on telegram.

## Usage
To use the project, follow these steps:

### main.py
1. Run the [`main.py`] script:
    ```
    python main.py
    ```
2. A GUI will open where you can place the image.
3. The output will be generated below the image in the GUI.

### old_main.py
1. Place the image file you want to extract text from in the project code.
2. Run the `old_main.py` script:
    ```
    python old_main.py
    ```
3. The extracted text will be displayed in the terminal output.

### bot_main.py
1. Run the `bot_main.py` script to start the Telegram bot:
    ```
    python bot_main.py
    ```
2. Use the Telegram bot (https://t.me/ocrscanner_bot) to send the image.
3. The bot will process the image and send back the extracted text.

## Contributing
Contributions to the OCR project are welcome. If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

