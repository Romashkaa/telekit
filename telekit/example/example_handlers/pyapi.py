import telekit

class PyAPIHandler(telekit.TelekitDSL.Mixin):
    
    TOTAL_ENDINGS = 8

    @classmethod
    def init_handler(cls) -> None:
        cls.on.message(commands=["pyapi"]).invoke(cls.handle)
        cls.analyze_string(script)

    def handle(self):
        self.visited_endings = set()
        self.start_script()

    def add_ending(self, ending_name: str):
        """API method called from DSL on_enter to mark an ending visited"""
        self.visited_endings.add(ending_name)

    def get_variable(self, name: str) -> str | None:
        match name:
            case "endings_to_find_count":
                return str(self.TOTAL_ENDINGS - len(self.visited_endings))

# ------------------------------------------------------
# Telekit DSL
# ------------------------------------------------------
#
# Tutorial on GitHub: https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md
#

script = """
@ main {
    title = "🏰 Adventure Quest"
    message = "Welcome, {{first_name}}! Can you discover all possible endings of this quest?\n\nYou have {{endings_to_find_count}} endings to find!"
    
    buttons {
        forest("Go to the Forest")
        cave("Explore the Cave")
        river("Follow the River")
        castle("Visit the Castle")
    }
}

@ forest {
    title = "🌲 Dark Forest"
    message = "You enter the dark forest. Paths diverge..."
    
    buttons {
        left_path("Take the left path")
        right_path("Take the right path")
    }
}

@ cave {
    title = "🕳️ Mysterious Cave"
    message = "The cave is damp and eerie. Something glows in the darkness..."
    
    buttons {
        investigate("Investigate the glow")
        retreat("Go back")
    }
}

@ river {
    title = "🌊 Rapid River"
    message = "The river is fast and dangerous. You see a boat and a bridge."
    
    buttons {
        boat("Take the boat")
        bridge("Cross the bridge")
    }
}

@ castle {
    title = "🏰 Old Castle"
    message = "The castle stands tall, abandoned but majestic."
    
    buttons {
        throne_room("Enter the throne room")
        tower("Climb the tower")
    }
}

@ left_path {
    title = "🌲 Left Path Ending"
    message = "You find a hidden treasure in the forest!"

    buttons {
        main("↺ Restart")
    }
    
    on_enter {
        add_ending("left_path")
    }
}

@ right_path {
    title = "🌲 Right Path Ending"
    message = "A wild wolf scares you away!"

    buttons {
        main("↺ Restart")
    }
    
    on_enter {
        add_ending("right_path")
    }
}

@ investigate {
    title = "🕳️ Cave Ending 1"
    message = "You found ancient runes!"

    buttons {
        main("↺ Restart")
    }
    
    on_enter {
        add_ending("investigate")
    }
}

@ retreat {
    title = "🕳️ Cave Ending 2"
    message = "You retreat safely but miss the treasure."

    buttons {
        main("↺ Restart")
    }
    
    on_enter {
        add_ending("retreat")
    }
}

@ boat {
    title = "🌊 River Ending 1"
    message = "The boat crashes, but you swim to shore."

    buttons {
        main("↺ Restart")
    }
    
    on_enter {
        add_ending("boat")
    }
}

@ bridge {
    title = "🌊 River Ending 2"
    message = "You safely cross and find a hidden path."

    buttons {
        main("↺ Restart")
    }
    
    on_enter {
        add_ending("bridge")
    }
}

@ throne_room {
    title = "🏰 Castle Ending 1"
    message = "You claim the throne. Victory!"

    buttons {
        main("↺ Restart")
    }
    
    on_enter {
        add_ending("throne_room")
    }
}

@ tower {
    title = "🏰 Castle Ending 2"
    message = "You fall from the tower. Ouch!"

    buttons {
        main("↺ Restart")
    }
    
    on_enter {
        add_ending("tower")
    }
}
"""