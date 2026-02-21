# Setting Up Obsidian

## Installation

Download Obsidian from [obsidian.md](https://obsidian.md) and install it for your platform (Windows, macOS, Linux).

## Creating a Vault

A **vault** is just a regular folder on your disk — Obsidian reads it and treats every file inside as a note.

1. Open Obsidian
2. Click [**Create new vault**](https://help.obsidian.md/vault)
3. Enter a name (e.g. `my-bot`)
4. Choose a location on your disk
5. Click **Create**

Your vault folder is now ready. All files you create in Obsidian will be stored there as plain files.

## Creating a Canvas

Canvas is a built-in Obsidian feature — no plugins needed.

To [create a new canvas](https://help.obsidian.md/plugins/canvas):

- Right-click any folder in the file explorer → **New canvas**
- Give it a name, e.g. `script`

## Finding the Canvas File on Disk

Your `.canvas` file is stored directly inside the vault folder:
```
my-bot/
└── bot.canvas
```

You can find the exact path by right-clicking the canvas in the file explorer → **Show in system explorer**.

This path is what you'll pass to Telekit Canvas:
```python
cls.analyze_canvas("path/to/my-bot/bot.canvas")
```

- [Next: Connecting Canvas](./connect.md)