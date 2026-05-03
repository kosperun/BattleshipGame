# Battleship in Python & Pygame

A fully functional Battleship game — human vs. computer — written in Python with Pygame.

[Video series on YouTube (in Russian)](https://www.youtube.com/playlist?list=PLn9_BS5G-UgruEeGmqgBTGtE0oN2nqBhL)

---

## Download & Play

Pre-built binaries are available on the [Releases](../../releases) page — no Python required.

| Platform | File |
|---|---|
| macOS | `BattleshipGame.dmg` |
| Windows | `BattleshipGame-windows.zip` |
| Linux | `BattleshipGame-linux.tar.gz` |

**macOS:** open the `.dmg`, drag the app to your Applications folder, then launch it from there.  
> First launch: if macOS blocks the app with "unidentified developer", run this in Terminal:
> ```bash
> xattr -cr /Applications/BattleshipGame.app
> ```
> Then launch the app normally.

**Windows:** unzip the archive and run `BattleshipGame.exe` inside the extracted folder.

**Linux:**
```bash
tar -xzf BattleshipGame-linux.tar.gz
chmod +x BattleshipGame/BattleshipGame
./BattleshipGame/BattleshipGame
```

---

## Run from Source

**Requirements:** Python 3.10+

```bash
# Clone the repository
git clone https://github.com/Perun108/BattleshipGame.git
cd BattleshipGame

# Install dependencies
poetry install --no-root

# Activate the virtual environment
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# Run the game
cd src && python main.py
```

---

## How to Play

- At the start, choose to place your ships **automatically** or **manually**
- Manual placement: click and drag on your grid to draw each ship (1–4 blocks)
- Use the **UNDO** button to remove the last placed ship
- Click on the computer's grid to fire — hits are marked with **X**, misses with a dot
- The computer fires back automatically after each of your shots
- First player to sink all 10 opponent ships wins

**Fleet:** 1×4-block, 2×3-block, 3×2-block, 4×1-block ships (10 total)

---

## Development

```bash
# Run tests
python -m pytest

# Run linter
pylint src/
```

---

## Screenshots

#### Place your ships
![image](https://user-images.githubusercontent.com/68146217/182445040-ab79406b-3994-44ed-88af-0cc0ff672002.png)

#### Drawing ships manually
![image](https://user-images.githubusercontent.com/68146217/182445250-b0190544-8bd9-410d-bdc0-a80a9f6085f2.png)

#### Game in progress
![image](https://user-images.githubusercontent.com/68146217/182609499-dc140a02-464a-4f3c-a203-5c1dea374b6c.png)

![image](https://user-images.githubusercontent.com/68146217/182609632-0b698694-2c8e-4ee6-bda4-83b6b113b5ec.png)

![image](https://user-images.githubusercontent.com/68146217/182609669-340121c9-2417-4e5a-921f-1d1d4065e2e6.png)

#### Game over
![image](https://user-images.githubusercontent.com/68146217/182608660-87a07f10-80dc-4a3c-bb1c-01e5b42efdf2.png)
![image](https://user-images.githubusercontent.com/68146217/182608828-9c0f01f1-eb67-4136-b235-3fb7370f472f.png)
