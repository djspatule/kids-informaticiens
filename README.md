# Kid Game - Linux Treasure Hunt

A local treasure hunt game for kids to discover computers, Linux basics, and
desktop navigation through small missions.

This project is designed for two children using separate Linux user sessions on
the same machine, without admin rights. The game watches for simple actions in
each child's own session and unlocks the next mission automatically.

## Goal

Create a fun, guided, spaceship-themed learning game where each child:

- finds files and folders
- opens and reads simple clues
- changes a few safe desktop settings
- learns basic Linux desktop habits
- progresses independently without spoiling the other child's game

At the end, the game reveals a final reward or secret message.

## Project choices

These decisions are already fixed for the first version:

- **Language:** Python
- **Loop style:** a small script checks progress every 2 seconds
- **Save format:** one JSON save file per child
- **Theme:** spaceship / space mission
- **Target desktop:** XFCE on Linux Mint
- **Future goal:** keep the design portable to GNOME later when possible
- **Permissions:** children do **not** have admin rights

## Why Python instead of Bash

Python is the better choice for this project.

### Python advantages

- Easy to read and maintain
- Better for JSON save files
- Cleaner logic for missions, conditions, and branching paths
- Easier to support different levels for different children
- Simpler to test and expand later
- Better string handling for notifications and clue text
- More portable across desktop environments

### Why not Bash for the main game

Bash is good for very small glue scripts, but it becomes harder to manage when
you need:

- structured progress tracking
- multiple children
- many missions
- retries and validation
- simple internationalization or vocabulary tuning
- future support for XFCE and GNOME differences

### Recommended approach

Use **Python for the game engine**.

Optionally use a few tiny Bash helpers later if needed for desktop-specific
checks or launcher integration.

## Core design

The game engine runs as a user-level background process inside each child's
session.

Every 2 seconds it:

1. reads the child's current state from JSON
2. checks whether the current mission is completed
3. if completed, marks it done
4. unlocks the next mission
5. shows a notification or clue
6. writes the updated state back to disk

Because each child has a separate Linux account and separate save file, they can
play in any order without spoiling each other.

## Main principles

### 1. No spoilers between kids

Each child has:

- their own save file
- their own mission folder
- their own progress
- their own notifications

No shared progress is required.

### 2. Very simple words

The clue text should use short, easy words.

This is especially important for Romy. Sentences should be closer to
early-reader level than standard game text.

Examples:

- "Open the blue folder."
- "Find the star file."
- "Click the picture."
- "Change the wall image."
- "Good job, captain!"

### 3. Different levels

The same engine can support different mission sets.

Suggested profiles:

- **Romy mode:** fewer words, more icons, shorter tasks, more visual clues
- **Oscar mode:** slightly longer clues, more steps, a bit more exploration

### 4. Safe actions only

Tasks should stay inside the user's session and home folder.

Good examples:

- open a folder
- find a file
- rename a file
- move a file
- change wallpaper
- create a text file
- open a terminal for a very simple command
- find hidden items only if introduced gently

Avoid anything that needs sudo, root access, or system-wide changes.

## Proposed folder layout

```text
kid-game/
├── README.md
├── game.py
├── config/
│   ├── global.json
│   ├── romy.json
│   └── oscar.json
├── saves/
│   ├── romy_state.json
│   └── oscar_state.json
├── missions/
│   ├── common/
│   ├── romy/
│   └── oscar/
├── clues/
│   ├── images/
│   └── text/
├── rewards/
└── logs/
```

## Save file example

```json
{
  "player": "romy",
  "profile": "easy",
  "current_mission": "mission_03",
  "completed": ["mission_01", "mission_02"],
  "last_check": "2026-04-11T10:00:00",
  "final_reward_unlocked": false
}
```

## Mission model

Each mission can be defined in JSON.

Example:

```json
{
  "id": "mission_03",
  "title": "Find the star",
  "description": "Open the Space folder and click the star file.",
  "check": {
    "type": "file_opened",
    "path": "~/Space/star.txt"
  },
  "success_message": "Star found. Good job, captain!",
  "next": "mission_04"
}
```

## Possible mission types

Good first mission types:

- `file_exists`
- `file_renamed`
- `file_moved`
- `folder_opened`
- `wallpaper_changed`
- `text_file_created`
- `simple_terminal_command_done`

Some checks will be easy and reliable. Others may need approximation depending
on the desktop environment.

## XFCE first, GNOME later

For version 1, target **XFCE only**.

Reason:

- easier to scope
- fewer desktop differences to handle now
- faster path to a playable prototype

To stay portable later:

- keep desktop-specific checks in separate helper modules
- isolate wallpaper or settings detection logic
- keep mission definitions independent from XFCE when possible

Example idea:

- `checks/base.py`
- `checks/xfce.py`
- `checks/gnome.py`

## Notifications

Use simple desktop notifications to tell the child what happens next.

Examples:

- "New mission! Go to the rocket folder."
- "Nice work! You found the moon key."
- "Mission done. Open the next clue."

If notification reliability becomes a problem, a small game window can be added
later.

## Suggested first missions

### Romy track

1. Open a folder with a rocket icon
2. Click a picture clue
3. Find a file named `star.txt`
4. Change the wallpaper
5. Move a file into a folder named `Ship`
6. Open the final treasure note

### Oscar track

1. Open the mission folder
2. Read a clue in a text file
3. Rename a file correctly
4. Move a file to the right folder
5. Create a text file with a given name
6. Open a terminal and run one very simple command
7. Find the final code word

## Technical notes

### Polling every 2 seconds

This is a good first implementation because it is:

- simple
- reliable
- easy to debug
- enough for a local game

It is not the most elegant event system, but it is the right trade-off for
version 1.

### JSON save files

JSON is a good fit because it is:

- human-readable
- easy to inspect
- easy to reset for testing
- easy to back up

### Running without admin rights

The engine should run fully inside the user's home directory and session.

Possible launch methods later:

- autostart entry in the child's session
- manual launcher icon on the desktop

## Good version 1 scope

A strong first version would include:

- one Python engine
- one shared mission format
- one easy profile
- one medium profile
- XFCE support only
- desktop notifications
- per-child JSON save file
- 5 to 7 missions per child
- one final reward screen or message

## Nice later improvements

- a small GUI instead of notifications only
- sound effects
- badge system
- save reset tool for parents
- mission editor
- GNOME support
- translations and easier French wording packs
- more visual clues for early readers

## Testing checklist

Before giving it to the kids, test:

- each mission can complete only in the correct session
- save files do not interfere with each other
- notifications appear reliably
- a child cannot skip to the end by accident
- resetting one child does not reset the other
- missions still work after logout/login

## Next build step

Recommended next deliverable:

1. create the mission JSON format
2. create a minimal Python loop
3. support 2 or 3 mission check types
4. show desktop notifications
5. test with one child profile first

## License

Private family project for now.
