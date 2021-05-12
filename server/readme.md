## BattleDot Server:

- Features:
    - This solution utilizes websockets, so clients can connect to the server through an online connection.
    - If a client leaves mid-game, their neighbors become matched together.
    - New players can join the server mid-game, however they must wait for the game to finish before playing.
- The log file can be found at `server.log` and contains a thorough description of all game actions.
- You may change the server's port in the `.env` file.
- As games can finish quite quickly, I have included a method of slowing down the game: modify the `UPDATE_DELAY_DELTA` constant in the `constants.py` file to introduce a delay to the server's actions. This will make it easier to test clients that join or leave mid-game.

# Instructions for Linux - Virtual Environment

1. Activate the virtual environment with `source venv/bin/activate`. Note: Python 3.3+ and venv is required.

2. Start the server with `python3 main.py` or `python main.py`.

# Backup Installation Instructions

(To keep the installation local, follow all 4 steps. Otherwise, start at step 3)

1. Delete the venv folder.

2. Create a new virtual environment with `python3 -m venv venv` and activate it with `source venv/bin/activate`.

3. Install the packages with `pip3 install -r requirements.txt` or `pip install -r requirements.txt`

4. Start the server with `python3 main.py` or `python main.py`.

- Created by Andrew Han
