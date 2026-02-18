# Clam Casino Server
Clam Casino is a single player card game that focuses on counting and deduction. The player is given a 5x5 grid of cards with hidden values from 0 to 3. Next to each row and column, the total sum of cards in the corresponding row / column is shown, alongside the number of zero cards. Turning over the first card rewards that number of points to the player, while subsequent cards multiply the player’s score by that value. If the player turns over a zero, their game is over. The player wins when all 2 and 3 cards have been turned over, as their score can no longer increase that round.

One of the unique aspects of this project was to handle all game logic in the backend, and rely on HTTP requests from a client in order to perform actions in the game. This makes cheating more difficult since critical gameplay information (such as the location of all of the 0 cards) is stored on the server.

The Clam Casino server currently runs in Python using [Flask](https://flask.palletsprojects.com/en/stable/).
The ["official" frontend](https://github.com/kazucroco/clam-casino-client) is not complete, has no documentation, and no releases. However, if you are familiar with Godot and are willing to build the project yourself, feel free to check it out.

## Installation Instructions
### Requirements
- Python 3.14+ (earlier versions of Python 3 may work, but do so at your own disgression)
- Some software to make HTTP requests to the server.
  - I use [Postman](https://www.postman.com/downloads/), but it requires an account and is definitely overkill for this application. I wouldn't *recommend* it but it's what I'm using anyway.

### Installation
These instructions are written by and for a Linux user. I will try to provide Windows instructions from memory, **but they are probably a little bit wrong**. You will need PowerShell and I think you need to [allow running scripts](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.5). It is a huge pain, sorry in advance.
- Clone this repository to a directory of your choice.
- Open the folder and create a Python virtual environment.
  - Linux: `python3 -m venv .venv`
  - Windows: `python -m venv .venv`
- Activate the new virtual environement.
  - Linux: `source .venv/bin/activate`
  - Windows: `./.venv/Scripts/Activate.ps1`
- Install the required packages.
  - Linux / Windows: `pip install -r requirements.txt`
- Run the server.
  - Linux / Windows: `flask --app clam_casino_server run`
- Success?

## Interaction and Endpoints
### New Game
- To start a new game, send a **POST** request to: `http://127.0.0.1:5000/new`
  - You should receive a game ID (i.e. `8735979417668`)
### Flip Cards
- To flip a card, send a **POST** request to: `http://127.0.0.1:5000/flip/{game_ID}` with the following JSON body:
  ```
  {
    "row": "0",
    "col": "0"
  }
  ```
  ... where `row` and `col` have values between 0 and 4.
- The response JSON should be as follows:
  ```
  {
    "card": 1,
    "over": false,
    "score": 1
  }
  ```
  - `card` is the value of the card you just turned over.
  - `over` indicates whether the game has ended (after all 2 and 3 cards are found, or a single 0 card is found).
  - `score` the player's current score.
  Once `over` is true, the game can no longer be interacted with and a new game has to be created.
## What's Missing
- The game is quite difficult to play or test with no user interface. For the sake of this concept, the complete game board is revealed to the server console each time a game is created. This can be used to verify proper behavior when flipping cards. 
- The server currently assumes correct input from the user at all times. Please be gentle.
- The code is horrendous, maybe even offensive to look at. Please be gentle.
