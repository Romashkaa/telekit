# Canvas Basics

This guide walks you through building bots visually using Telekit Canvas mode.

## How It Works

Every **node** in your canvas becomes a **scene** — a message your bot sends.
Every **arrow** between nodes becomes a **button** the user can tap.

<table> <tr>
    <td><img src="/docs/images/canvas/example.png" alt="Canvas Example 1" width="500"></td>
</tr> </table>

## The Main Scene

The **topmost node** automatically becomes the `main` scene — the first screen your bot shows when the user sends `/start`.

<table> <tr>
    <td><img src="/docs/images/canvas/example2.png" alt="Canvas Example 2" width="500"></td>
</tr> </table>

> [!WARNING]
> Keep your main node visually at the top of the canvas to make the flow easy to read.

## Node Format

Each node can be written in two ways:

### Plain Text

```
👋 Welcome to my bot!

Choose an option below:
```

The entire text becomes the message body. The button label (shown in the parent scene) is generated automatically from the first line, trimmed to 24 characters.

### Title + Message

```
🛍 Our Services
---
We offer the following:
- Web Development
- Mobile Apps
- Consulting
```

Everything **above** `---` becomes the **title** and the **button label**.
Everything **below** `---` becomes the **message body**.

### Example 

<table> <tr>
    <td><img src="/docs/images/canvas/example3.png" alt="Canvas Example 3" width="500"></td>
</tr> </table>

## Navigation

### Arrows

Draw an arrow from node **A** to node **B** — Telekit will add a button in scene A that navigates to scene B.

- The button label is taken from node B (its title, or auto-generated from the first line)
- You can draw multiple arrows from one node to create multiple buttons

<table> <tr>
    <td><img src="/docs/images/canvas/example4.png" alt="Canvas Example 4" width="500"></td>
</tr> </table>

### Going Back

To add a "back" button, simply draw an arrow from the child node back to the parent. It will appear as a regular button labeled with the parent's title or first line.

<table> <tr>
    <td><img src="/docs/images/canvas/example5.png" alt="Canvas Example 5" width="500"></td>
</tr> </table>

## Groups and Colors

Groups are **ignored** by the parser — they are purely visual. Use them freely to organize sections of your canvas without affecting bot behavior.

Node colors are also **ignored**. Use them as visual markers for yourself.

## Full Example

Here is a simple FAQ bot canvas:

<table> <tr>
    <td><img src="/docs/images/canvas/example6.png" alt="Canvas Example 6" width="500"></td>
</tr> </table>