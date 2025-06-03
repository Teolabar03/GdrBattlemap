# GdrBattlemap

**GdrBattlemap** is a lightweight, customizable battlemap tool designed for tabletop RPGs such as Dungeons & Dragons. Built using Pygame, it allows you to load custom background images, draw grids, place colored tokens, and manage the battlefield in an intuitive visual interface.

The images used are for placeholder purposes only. The rights belong to the respective image owners and must be replaced if the project is used.


---

## Features

- Load custom background images (maps)
- Toggle grid display on/off
- Resize grid cells dynamically
- Add and remove colored tokens
- Drag and snap tokens to grid cells
- Pick colors using a color picker or HEX input
- Fullscreen support
- Simple and user-friendly interface

---

## Installation

### Requirements

- Python 3.7+
- Tkinter (usually included with Python)
- Pygame (Install dependencies using pip: pip install pygame)
- It requires to be run with administrator privileges in order to access the C: folder to save the .json.

### Commands

| Action             | Description                             |
| ------------------ | --------------------------------------- |
| **F**              | Toggle fullscreen                       |
| **Left Click**     | Interact with UI or place/select tokens |
| **Drag Token**     | Move a token on the map                 |
| **Enter HEX Code** | Apply a custom color in HEX format      |
| **DEL Button**     | Delete selected token                   |
| **Load Image**     | Load a custom background map            |
| **Toggle Grid**    | Show or hide the grid                   |
| **+ / - Buttons**  | Increase or decrease grid cell size     |
| **Color Picker**   | Open color picker for token color       |


### Clone the repo

```bash
git clone https://github.com/Teolabar03/GdrBattlemap.git
cd GdrBattlemap
