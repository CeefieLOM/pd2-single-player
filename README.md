# PD2 Single Player Unlock

A small script that brings back the **Single Player** (and **Other Multiplayer**)
buttons in a Project Diablo 2 install, so you can play offline.

It changes 7 bytes in your own `ProjectDiablo.dll`. It ships no game files, and
you can undo it at any time.

> Community tool. Not made or endorsed by Blizzard Entertainment.

## Requirements

- A normal Project Diablo 2 install (Diablo II 1.13c files in a `ProjectD2` folder).
- Python 3.8 or newer.
  - **Windows:** install it from [python.org](https://www.python.org/downloads/)
    and tick **"Add python.exe to PATH"** during setup.
  - **Linux:** usually already installed (`python3 --version`).

## How to use

### 1. Download the script

Download [`pd2_single_player.py`](pd2_single_player.py) (open it, then use
**Download raw file**) and save it anywhere, e.g. your Downloads folder.

### 2. Close Project Diablo 2

Close the game and the PD2 launcher first.

### 3. Run it on your `ProjectD2` folder

**Windows** — open *Command Prompt* in the folder where you saved the script, then run
(change the path if PD2 is installed elsewhere):

```bat
python pd2_single_player.py "C:\Program Files (x86)\Diablo II\ProjectD2"
```

**Linux (Wine/Lutris)** — point it at the `ProjectD2` folder inside your Wine prefix:

```sh
python3 pd2_single_player.py "$HOME/Games/project-diablo-2/drive_c/Diablo II/ProjectD2"
```

You should see:

```
Backup: ...\ProjectDiablo.dll.singleplayer-backup
Single Player unlocked in ...\ProjectDiablo.dll.
```

### 4. Start the game with `Game.exe`, not the PD2 launcher

The PD2 launcher puts its own `ProjectDiablo.dll` back every time it starts,
which removes the unlock. Start the game directly instead:

- **Windows:** create a shortcut to `ProjectD2\Game.exe` and add ` -3dfx` to the
  end of its *Target*, e.g.
  `"C:\Program Files (x86)\Diablo II\ProjectD2\Game.exe" -3dfx`
- **Linux:** run `Game.exe -3dfx` with your Wine prefix, e.g.
  `WINEPREFIX=... wine "…/ProjectD2/Game.exe" -3dfx`

The main menu now shows **Single Player**.

## Other commands

| Command | What it does |
| --- | --- |
| `python pd2_single_player.py FOLDER --check` | Shows whether Single Player is locked or unlocked. Changes nothing. |
| `python pd2_single_player.py FOLDER --revert` | Puts PD2's original setting back (Single Player hidden). |

If you leave out `FOLDER`, the script uses the folder you run it from.

## After a PD2 update

PD2 updates (and starting the PD2 launcher) replace `ProjectDiablo.dll`.
Just run the script again. If an update changes the files in a way the script
does not recognise, it stops with a message and changes nothing.

## Please don't play online with it

Use the unlocked `ProjectDiablo.dll` for offline play only. If you go online,
start through the PD2 launcher, which restores the original file, or run
`--revert` first.

## How it works

At startup `ProjectDiablo.dll` applies a list of byte patches to the game's
DLLs. The first one rewrites the main-menu code in `D2Launch.dll` (offset
`0x17ec4`) from the original `jl; push 0x624` (`7c 0a 68 24 06 00 00`) into a jump
(`e9 06 01 00 00 90 90`) that skips creating the Single Player and Other
Multiplayer buttons.

The script changes only that entry's 7 data bytes back to the original code.
PD2 still applies and checks the rest of its list, so nothing else changes.

Safety checks:

- The entry is found by its exact contents, not a fixed position, and must
  appear exactly once.
- `D2Launch.dll` must be the exact known 1.13c build (SHA-256 checked).
- A backup (`ProjectDiablo.dll.singleplayer-backup`) is made before the first change.
- The new file replaces the old one in a single step.

## Troubleshooting

| Message | Meaning |
| --- | --- |
| `No ProjectDiablo.dll and D2Launch.dll in …` | The path is not your `ProjectD2` folder. |
| `Unrecognised D2Launch.dll` | Your game files differ from the supported build. Nothing was changed. |
| `PD2's menu patch entry was not found exactly once` | This PD2 version is not supported yet. Nothing was changed. |
| `Failed: [Errno 13] Permission denied` | On Windows, run *Command Prompt* as administrator if PD2 is under `Program Files`. |
| Single Player is still missing | You probably started the PD2 launcher, which restored its file. Run the script again and start `Game.exe` directly. |
