from .buildtext.styles import *

Group = Composite

__all__ = [
    "Composite", "Group",
    "Styles",

    "Sanitize",
    "NoSanitize",

    "Bold",
    "Italic",
    "Underline",
    "Strikethrough",
    "Code",
    "Spoiler",

    "Link",
    "UserLink",

    "Quote",
    "Python",

    "label_cheatsheet"
]

def label_cheatsheet():
    """
    Hi! You can use any of these emojis in button labels:

    ### Navigation:
        `« Back`
        `Next »`
        `← Back`
        `Next →`
        `↺ Restart`

    ### "Pop-ups":
        `Hmm ？`
        `Okay ✓`

    ---

    [ Viiiiiiing Ultra Mega Studio™®©℗ ]  
    Romashka's Officially Licensed™ "Label Cheatsheet™™®"  
    Limited Platinum Diamond Gold Edition 3000™  
    (c) 2025 All Rights Reserved™®℗  
    Featuring Patented Button Magic™ & Secret Emoji™ Technology™
    
    (no)"""
    print(
"""

---------------------------------------------------------------------------

You can use any of these emojis in button labels:

    ### Navigation:
        `« Back`
        `Next »`
        `← Back`
        `Next →`
        `↺ Restart`

    ### Pop-ups:
        `Hmm ？`
        `Okay ✓`

---------------------------------------------------------------------------

""")