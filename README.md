# SmutSmiter5000 

The SmutSmiter5000 (name subject to change) is a script written to ease library moderation in Space Station 13 on the [/tg/station](https://github.com/tgstation/tgstation) codebase through [AtlantaNed's old StatBus](https://github.com/nfreader/slimbus).

Don't judge the code quality too hard, it was first written as a script in a very short about of time and then hastily and forcefully remade.

## Prerequisites

If you do not wish to download Python, I included an executable for Windows [here](https://github.com/RigglePrime/smutsmiter5000/releases).

This project was written for Python3 and there is no official Python2 support.

Install packages located in `requirements.txt`. This can be done using `pip install -r requirements.txt` (`pip3` on Linux)

## Running the code

1. Go to StatBus and log in
2. Locate your cookies.
    - Chrome: F12 -> Application -> Storage -> Cookies
    - Firefox: F12 -> Storage -> Cookies
3. Get that PHPSESSID cookie value
4. Run the script (pick one of the options below)
    - Run the script with positional arguments. (`python main.py <cookie value> <book id>`)
    - Run the script (`python main.py`) and input the values when prompted
