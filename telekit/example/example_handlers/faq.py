import telekit

class FAQHandler(telekit.TelekitDSL.Mixin):
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
#
# Tuturial on GitHub: https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md
#

guide = """
$ timeout {
    time = 5; // optional
    message = "🤔 Are you here? (Yes, 5 seconds is very short, but this ensures you can see that the feature works)"; // optional
}

@ main {
    title   = "📖 FAQ - Frequently Asked Questions";
    message = "Here are answers to common questions to help you get started:";
    buttons {
        developers;    // "Who are developers"
        documentation; // "📚 Documentation"
    }
}

@ developers("Who are developers") {
    title   = "👨‍💻 Developer";
    message = "This bot was spellcrafted by [Telekit Wizard](https://t.me/+WsZ1SyGYSoI3YWQ8) 🪄✨";
    parse_mode = "markdown";
    buttons { back("« Back") }
}

@ documentation {
    title   = "📚 Documentation";
    message = "Here you can find helpful guides and references: https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md";
    buttons (2) { 
        back("« Back");
        developers("Developers »");
    }
}

/*

« Back
  Next »
✓ Okay

*/
"""
