# 
# Copyright (C) 2026 Romashka
# 
# This file is part of Telekit.
# 
# Telekit is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version.
# 
# Telekit is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See 
# the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License 
# along with Telekit. If not, see <https://www.gnu.org/licenses/>.
# 

from ._buildtext.styles import *

__all__ = [
    "TextEntity",
    "StaticTextEntity",
    "EasyTextEntity",

    "Styles",

    "Group",
    "Stack",

    "Escape",
    "Raw",

    "Bold",
    "Italic",
    "Underline",
    "Strikethrough",
    "Code",
    "Spoiler",

    "Link",
    "Mention",
    "UserLink",
    "BotLink",

    "Quote",
    "Language",
    "Python",

    "EncodeURL",

    "label_cheatsheet"
]

def label_cheatsheet():
    """
    You can use any of these emojis in button labels:

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