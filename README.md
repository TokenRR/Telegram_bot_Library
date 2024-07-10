# Telegram bot for for an online library
## Cloning a repository

To download this code from GitHub, open a terminal and run the following commands:
```sh
git clone https://github.com/TokenRR/Telegram_bot_Library.git
cd Telegram_bot_Library
```

## Installing dependencies

Create a virtual environment and install dependencies:
```sh
python -m venv venv
source venv/bin/activate  # For Windows, use venv\Scripts\activate
pip install -r requirements.txt
```

## Setting up the configuration
Open the `config.py` file and change the bot token to your own:
```python
TOKEN='your-token-here'
```

## Start program
To start the program, execute the following command:
```sh
python main.py
```