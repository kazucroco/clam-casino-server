# Clam Casino
Clam Casino is a single player card game based on Voltorb Flip which focuses on counting and deduction. The player is given a grid of cards with hidden values from 0 to 3. Next to each row and column, the total sum of cards in the corresponding row / column is shown, alongside the number of zero cards. Turning over the first card rewards that number of points to the player, while subsequent cards multiply the player’s score by that value. If the player turns over a 0, their score is set to 0, and the game is over. The player wins when all 2 and 3 cards have been turned over, as their score can no longer increase that round.

One of the primary goals of this project was to separate the frontend and backend. All game state and logic is stored and calculated on a Python server, and player inputs are performed through HTTP requests. This ensures the player cannot simply see the location of all 0 cards (or other hidden gameplay information) by inspecting the page. While there are occasions where the entire board can be calculated based on the given information, the game often forces the player to take a chance between cards, adding to its appeal.

The Clam Casino server currently runs in Python using [Flask](https://flask.palletsprojects.com/en/stable/). This repository in particular provides a `Dockerfile` and `docker-compose.yml` for easy production setups, using [Gunicorn](https://gunicorn.org/) as a WSGI server, and [Caddy](https://caddyserver.com) as a web server and proxy to manage the incoming requests.

### [**Try it out!**](https://kitsu.croco.dev)

## Server Installation and Setup
**Note:** This is for self-hosting your own instance! If you are just looking to play the game, this is not what you're looking for. This assumes you have a computer to run it on and at least a little bit of command line experience.
### Requirements
- [Docker](https://www.docker.com/get-started/) (v29.3 is tested, older versions may work)
- **For local hosting / testing:** a modern, Chromium-based browser.
	- Other browsers (like Firefox) are perfectly capable of interacting with the server, it is much more difficult to bypass the self-signed certificate warning.
- **For remote hosting / public servers:** a domain you own which points to the server you wish to host the Clam Casino server on.
	- Setting up A records, port forwarding, etc, are out of scope of this guide. The rest of the instructions assume you are only testing locally.
### Installation Instructions
- Clone this repository to a directory of your choice.
- Navigate to the directory in a terminal (PowerShell, Konsole, etc.).
- Run `docker compose up -d --build`
	- This will create the containers for the game server and the Caddy proxy and run them in the background.
	- If this fails, it is likely that you are already running other servers on ports `80` or `443`. You can change the port mapping in `docker-compose.yml` to use alternative ports if needed. For example, change `80:80` to `8080:80` and `443:443` to `8443:443` to host the web server on ports `8080` and `8443`.
### Configuration
#### Game
- Game configuration (i.e. max score per level) is done through the environment variables set in the `docker-compose.yml` file. To modify the configuration, open the file in your favorite text editor and change the values of the variables. More information about their purpose is written in the file's comments.
#### Server
- In `docker-compose.yml`, enter your website's URL into the value of `ALLOWED_ORIGINS`. Do **NOT** include a slash at the end, or you may encounter issues. Correct example: `ALLOWED_ORIGINS=https://kitsu.croco.dev`
	- You can allow multiple origins by separating the values with a comma.
- In `Caddyfile`, on the first line, change `localhost` to the same domain that you use in your `ALLOWED_ORIGINS` **without** the `https://`.

> After changing configuration, rebuild the container by running `docker compose up -d --build` again.

## Interaction and Endpoints
The server addresses in this section are all written in terms of `kitsu.croco.dev`. Naturally, interactions with your own server would use your domain / IP. For local hosting, this would be `localhost`.
### New Game
- To start a new game, send a **POST** request to: `https://kitsu.croco.dev/new`
	- Your request should be an `application/json` object. If empty, a level 0 game will be requested from the server.
	- You can modify this request by changing the value of `"level"` in the body.
```json
{
	"level": 0
}
```
> Level values start from 0 and go up to 7. For display only, the official frontend adds 1 to all levels. 

- Assuming a successful request, you will get a response similar to the following:
```json
{

	"game_id": "8740710668361",
	"level": 0,
	"pscore": 56,
	"size": 6,
	"totals": {
		"cols": [[3,3], [7,1], [8,0], [5,1], [7,1], [6,0]],
		"rows": [[9,1], [5,1], [5,3], [6,0], [6,0], [5,1]]
	}
}
```
- `game_id` is a unique identifier for this game session, and is used by the client to make input requests to the server.
- `level` is the difficulty level of the board (should be the same as requested)
- `pscore` is the user's persistent score, which is the total score they have accumulated on this server.
	- When the client interacts with the server, the server will check for a `ccid` cookie containing a unique identifier for the player. If one is not found, the server will generate a new one and send it with the response.
	- After each game is completed, the server will add the player's final score to a database. 
- `size` is the number of rows / columns in the board (will always be square).
	-  `6` is the default and represents a 6x6 grid.
- `totals` is an object containing the `[point, zero]` totals for each respective row and column.
	- Rows and columns are zero-indexed, and counted from left to right / top to bottom.
	- i.e) `rows[0]` is `[9,1]`, indicating that the sum of digits for cards in the first row is 9, and the row contains a single 0 card.
### Flip Cards
- To flip a card, send a **POST** request to: `https://kitsu.croco.dev/flip/{game_ID}` with the following JSON body:
  ```json
  {
    "row": 0,
    "col": 0
  }
  ```
  ... where `row` and `col` have values less than `size`, and represent the grid coordinates for the card which the player intends to turn over (zero-indexed).
- The response should be as follows:
```json
{
	"card": 1,
	"flip_lut":  [[1,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0]
	],
	"over": false,
	"pscore": 0,
	"score": 1,
	"solution": []
}
```
- `card` is the value of the card which was just turned over.
- `flip_lut` is a [lookup table](https://en.wikipedia.org/wiki/Lookup_table) of which cards have been flipped already. 0 represents unflipped and 1 is flipped.
- `over` indicates whether the game has ended (after all 2 and 3 cards are found, or a single 0 card is found).
	- Once a game is over, it can no longer be interacted with. All future inputs will return a 404 error, as the game has been deleted from the server.
- `pscore` is the player's persistent score (as explained in the `/new` section).
	- `pscore` is not added to until the game has been completed. If the player loses the game, `pscore` remains unchanged.
- `score` is the player's current score for this game session.
- `solution` is an object reserved for the complete board solution once the game is over. Until then, it is an empty list.
	- If the environment variable `CLAMCASINO_DEBUG` is set to 1, then the `solution` key will display the complete board regardless of whether the game is over or not.
	- The board solution follows the same format as `flip_lut`, except each value in the array is the actual value of the card it represents.

## File Structure
- `clam_casino_server/`: Contains all classes and objects for the API endpoints and actual game logic.
- `Caddyfile`: Configuration for Caddy, which is the web server directly handing requests.
- `Dockerfile`: Configuration for the Clam Casino server container image.
	- If you wish to make configuration changes to the Clam Casino server, please do so in `docker-compose.yml` instead.
- `docker-compose.yml`: Contains configuration for both the Clam Casino and the Caddy containers. 
	- Most gameplay configuration changes (such as changing score limits, etc), should be done in the `environment:` section under the `clam_casino_server` container.
