# Text Styling

This document lists all available style classes and their purpose:

- `Bold` - makes text bold (`*text*` in Markdown, `<b>text</b>` in HTML)
- `Italic` - makes text italic (`_text_` in Markdown, `<i>text</i>` in HTML)
- `Underline` - underlines text (`__text__` in Markdown, `<u>text</u>` in HTML)
- `Strikethrough` - strikes through text (`~~text~~` in Markdown, `<s>text</s>` in HTML)
- `Code` - formats inline code (`` `text` `` in Markdown, `<code>text</code>` in HTML)
- `Python` - formats Python code blocks (``` ```python ... ``` ``` in Markdown, `<pre language="python">...</pre>` in HTML)
- `Spoiler` - hides text until clicked (`||text||` in Markdown, `<span class="tg-spoiler">text</span>` in HTML)
- `Quote` - formats text as a quote block (`text\n` in Markdown (nothing), and `<blockquote>text</blockquote>` in HTML)
- `Escape` - escapes HTML/Markdown tags to safely include user input
- `Raw` - prevents escaping of HTML/Markdown tags
- `Link` - creates a clickable link (`[text](url)` in Markdown, `<a href="url">text</a>` in HTML)
- `UserLink` - creates a link to a user with an optional pre-filled (default) message
- `BotLink` - creates a link to bot, optionally including a pre-filled start command