## BattleDot Client:

- Open as many instances of this client as players in the game. To prevent games from starting prematurely, you must type "R" and press "Enter" on all connected clients before the game will commence.
- As games can finish quite quickly, I have included a method of slowing down the game: modify the `UPDATE_DELAY_DELTA` constant in the `constants.py` file to introduce a delay to the client's actions. This will make it easier to test clients that join or leave mid-game.
- Features:
    - This solution utilizes websockets, so the connection can work between multiple computers. This will require an adjustment to the websocket URL found in the `.env` file.
    - Clients attack co-ordinates randomly, however they will remember their previous targets and will not attack the same co-ordinate twice unless their opponent changes. This increases the liklihood they will get a hit over time.
- This client does not output a log, although thorough logs of important client actions are included in the BattleDot server's log file.

# Instructions for Linux - Virtual Environment

1. Activate the virtual environment with `source venv/bin/activate`. Note: Python 3.3+ and venv is required.

2. Start the client with `python3 main.py` or `python main.py`

# Backup Installation Instructions

(To keep the installation local, follow all 4 steps. Otherwise, start at step 3)

1. Delete the venv folder.

2. Create a new virtual environment with `python3 -m venv venv` and activate it with `source venv/bin/activate`.

3. Install the packages with `pip3 install -r requirements.txt` or `pip install -r requirements.txt`

4. Start the client with `python3 main.py` or `python main.py`. If using a virtual environment, please remember to activate the virtual environment for each client.

- Created by Andrew Han