# Friends Like Twins

Friends Like Twins is a two-player friendship quiz built with Python and
Pygame. Each friend answers questions about themselves and then guesses the
other person's answers. The game finishes with a score out of 10 and a short
friendship summary.

## Run the prebuilt game

The included executable is for 64-bit Linux (x86-64). It does not require
Python or Pygame to be installed.

From the repository directory, run:

```bash
chmod +x dist/friends_like_twins
./dist/friends_like_twins
```

The executable is not compatible with Windows or macOS. On those systems, run
the game from source instead.

## Run from source

Python 3.11 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
python friends_like_twins.py
```

To start the game again later:

```bash
source .venv/bin/activate
python friends_like_twins.py
```

## How to play

1. Enter the names of two friends.
2. Pass the computer to the person named on the screen.
3. Each friend answers 10 questions about themselves.
4. Each friend guesses the other person's answers.
5. Compare the final scores and friendship summary.

## Build the Linux executable

Install the project and PyInstaller, then build from the included specification:

```bash
python -m pip install .
python -m pip install "pyinstaller>=6.21.0"
pyinstaller --clean friends_like_twins.spec
```

The rebuilt executable will be available at `dist/friends_like_twins`.
