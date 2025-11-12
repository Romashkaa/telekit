import telebot.types # type: ignore
import telekit

class GuideHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.message(commands=["faq"]).invoke(cls.start_script)
        cls.analyze_source(guide)

    # If you want to add your own bit of logic:
    
    # def start_guide(self):
    #     # Your logic
    #     super().start_guide()

# ------------------------------------------------------
# Telekit DSL
# ------------------------------------------------------

guide = """
// -----------------------------------------------------
//  BASIC CONFIG BLOCK
// -----------------------------------------------------
// `$ config { ... }` — defines general metadata about your faq script.
$ config {
    timeout = 10 // `chain.set_timeout()` in seconds
}

@ timeout {
    title   = "🤯 Timeout. Send /faq again";
    message = "I know 10 seconds is too short, but this is just a demo of the feature. You can disable it entirely if you want";
}

// -----------------------------------------------------
//  MAIN BLOCK (FIRST PAGE)
// -----------------------------------------------------
// `@ main` — entry point for the faq.
@ main {
    title   = "📖 FAQ - Frequently Asked Questions"; // Heading / Title (Bold)
    message = "Here are some common questions and answers to help you get started:";

    // `buttons[2]` — max 2 buttons per row
    buttons[2] {
        menu_example("🧺 Menu Example");   // Opens @menu_example
        photo_demo("🖼 Image Example");    // Opens @photo_demo
        navigation("🧭 Navigation Demo");  // Opens @navigation
    }
}

/*
--------------------------------------------------------
📘 BLOCK STRUCTURE OVERVIEW
--------------------------------------------------------

Each block represents one "screen" (page) of your bot faq.
 
Required fields:
    title: str        - Appears at the top of the page (bold)
    message: str      - Main text shown below the title

Optional fields:
    buttons { ... }   - Defines clickable options for navigation
    image: str        - URL of an image to display under the text
    use_italics: bool - Apply italics to the message (default: False)
    parse_mode: str   - Text formatting mode; can be:
                        "HTML" (default) or "Markdown"

Example:
    @ example_block {
        title   = "🧩 Example Page";
        message = "Hello, <b>Romashka</b>!";
        image   = "https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450";
        use_italics = True;
        parse_mode  = "HTML";

        buttons[2] { // `row_width = 2` (1 by default)
            something("➡️ Next Step");
            back("⬅️ Back");
        }
    }


// -----------------------------------------------------
// 🔮 MAGIC BUTTONS
// -----------------------------------------------------

Special keywords that trigger built-in actions:

    back     - uses stack to return to previous page

 // These buttons don't require a direct link to a block;
 // their behavior is handled automatically by the guidekit engine.

Examples:
	@ example_magic {
	    title   = "✨ Magic Buttons Demo";
	    message = "Below are examples of built-in system buttons.\nTry clicking them to see what happens!";

	    buttons {
	        back("⬅️ Go Back"); // returns to previous page (FILO stack)
	    }
	}
*/

// -----------------------------------------------------
//  MENU EXAMPLE
// -----------------------------------------------------
// How to build structured, multi-page menus.

@ menu_example {
    title   = "⚙️ Bot Menu";
    message = "A common use case — menus.\nYou can use lists, emojis, and multiple options to guide the user.";

    buttons[2] {
    	back("⬅️ Back");              // Automatically goes to previous page
        tips_setup("💡 Setup Tips");  // Opens @tips_setup
    }
}

@ tips_setup {
    title   = "💡 Setup Tips";
    message = "— Use clear variable names for readability.\n— Test each page separately before publishing.\n— Always include `@ main {}` at the top of your FML file.";
    buttons {
        back("👌 Got it");
    }
}

// -----------------------------------------------------
//  IMAGE / PHOTO DEMO
// -----------------------------------------------------

@ photo_demo {
    image   = "https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450";
    title   = "🖼 Photo Example";
    message = "This page demonstrates how an image could be placed below this text.";
    buttons {
        back("⬅️ Back");
    }
}

// -----------------------------------------------------
//  NAVIGATION DEMO
// -----------------------------------------------------
// Shows how multiple branches and back links interact.
@ navigation {
    title   = "🧭 Navigation Demo";
    message = "This demonstrates multiple choices and auto-back handling.";
    buttons[2] {
        option_a("A: Path One");
        option_b("B: Path Two");
        back("⬅️ Back");
    }
}

@ option_a {
    title   = "Path A";
    message = "You chose option A.";
    buttons {
        back("⬅️ Return");
    }
}

@ option_b {
    title   = "Path B";
    message = "You chose option B.";
    buttons {
        back("⬅️ Return");
    }
}"""