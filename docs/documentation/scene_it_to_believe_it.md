# 🪄 The Ultimate Telekit Bot-Generation Prompt

Copy everything in the code block below, fill in `[BOT DESCRIPTION]` at the bottom, and hand it to any LLM. You'll get back a ready-to-run Telekit DSL script.

# Telekit DSL Content Formatting Rules

Reference: [Telekit DSL Syntax](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md)

You are generating content for a Telegram bot in **Telekit DSL** format. Follow the rules below.

---

## 1. Message Formatting

1. For any scene, use `title` + `message` rather than plain `text` — this
   gives a structured look (heading + body).
2. Always start `title` with a single relevant emoji: `"🏨 Name"`,
   `"📖 FAQ"`. Don't repeat the same emoji on buttons within that scene.
3. For text longer than one sentence, use a multiline string (backtick);
   Telekit automatically normalizes indentation:
   ```js
   message = `
       First line.
       Second line.
   `
  ```
4. If any formatting is needed (bold/italic/links), always set
   `parse_mode = "markdown"` or `"html"` — otherwise the markup won't render.
5. In markdown mode, escape special characters in plain text (period,
   hyphen, etc. — `\\.`, `\\-`) when they aren't part of intended markup.
6. Format lists with `-` or `•`, one item per line.
7. For personalization, use `{{first_name}}`, `{{username}}`, etc., always
   with a default value when the field isn't guaranteed to be set:
   `{{last_name:friend}}`.
8. Keep `message` concise: 3–6 short lines beats one dense paragraph.

---

## 2. Button Placement and Order

### General rule for `back()`

`back()` always sits at the **bottom** of the layout — never in the middle
of an options list, and never at the top.

- If `back()` shares a row with other buttons, it's always on the **left**.
- If `next()` is in the same row, it's always on the **right**.
- Intermediate/central actions (link, a specific option) go between them.

### Valid layouts

**Pattern 1 — Back | Next**
(when the scene has no options of its own)
```js
buttons(2) {
    back("« Back")
    next("Next »")
}
```

**Pattern 2 — options list + Back | Next below**
(when there are options plus an explicit forward step)
```js
buttons(1) {
    opt_1("Option 1")
    opt_2("Option 2")
}
buttons(2) {
    back("« Back")
    next("Next »")
}
```

**Pattern 3 — options list + Back below**
(when there are options but no "next" step)
```js
buttons(1) {
    opt_1("Option 1")
    opt_2("Option 2")
    back("« Back")
}
```

**Pattern 4 — Back | Option | Next**
(when there's one central action paired with navigation)
```js
buttons(3) {
    back("« Back")
    opt("Option")
    next("Next »")
}
```

### Additional layout rules

- Navigation buttons to sub-sections (transitions to child scenes) come
  first, in order of importance.
- `link()` (external URLs) goes next to `back`/`next`, in the same bottom
  row block — not mixed into the options list.
- `suggest()` for suggested input goes before the main action button.
- Use `row_width`:
  - 2 buttons per row when there are 3–4 total;
  - 3 buttons per row for uniform short actions (`back` / option / `next`).
- Avoid more than 2 rows of buttons per screen unless strictly necessary.