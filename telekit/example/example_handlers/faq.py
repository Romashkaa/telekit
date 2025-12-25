import random

import telekit

class FAQHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.message(commands=["faq"]).invoke(cls.start_script)
        cls.analyze_source(guide)
        
        # cls.display_script_data()

    def handle(self) -> None:
        self.start_script()

    def get_variable(self, name: str) -> str | None:
        match name:
            case "random_lose_phrase":
                phrases = [
                    "Keep going, you're doing great!",
                    "Don't give up!",
                    "Almost there, try again!",
                ]
                return random.choice(phrases)
            case _:
                # fallback to built-in variables if None
                return None

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
    time = 20;
}

@ main {
    title   = "🎉 Fun Facts Quiz";
    message = "Hello, {{first_name}}. Test your knowledge with 10 fun questions!";

    buttons {
        next("Start Quiz");
    }
}

@ question_1 {
    title   = "🐶 Question 1";
    message = "Which animal is the fastest on land?";
    buttons {
        _lose("Elephant");
        next("Cheetah");       // correct answer
        _lose("Horse");
        _lose("Lion");
    }
}

@ question_2 {
    title   = "🍫 Question 2";
    message = "From which product is chocolate made?";
    buttons {
        _lose("Cocoa powder");
        next("Cocoa beans");   // correct answer
        _lose("Cocoa butter");
        _lose("Cocoa drink");
    }
}

@ question_3 {
    title   = "🌌 Question 3";
    message = "Which planet is known for its prominent rings?";
    buttons {
        _lose("Jupiter");
        next("Saturn");        // correct answer
        _lose("Mars");
        _lose("Neptune");
    }
}

@ question_4 {
    title   = "🦎 Question 4";
    message = "Which animal can change the color of its skin?";
    buttons {
        next("Chameleon");     // correct answer
        _lose("Crocodile");
        _lose("Turtle");
        _lose("Snake");
    }
}

@ question_5 {
    title   = "🍌 Question 5";
    message = "Which vitamin is most abundant in a banana?";
    buttons {
        _lose("Vitamin C");
        next("Vitamin B6");    // correct answer
        _lose("Vitamin D");
        _lose("Vitamin A");
    }
}

@ question_6 {
    title   = "🎨 Question 6";
    message = "Which artist painted the 'Mona Lisa'?";
    buttons {
        next("Leonardo da Vinci"); // correct answer
        _lose("Pablo Picasso");
        _lose("Vincent van Gogh");
        _lose("Michelangelo");
    }
}

@ question_7 {
    title   = "🎵 Question 7";
    message = "Which musical instrument has 88 keys?";
    buttons {
        _lose("Guitar");
        _lose("Harmonica");
        next("Piano");          // correct answer
        _lose("Saxophone");
    }
}

@ question_8 {
    title   = "🧩 Question 8";
    message = "How many faces does a cube have?";
    buttons {
        _lose("6");
        next("6");             // correct answer
        _lose("8");
        _lose("12");
    }
}

@ question_9 {
    title   = "🌊 Question 9";
    message = "Which is the largest ocean on Earth?";
    buttons {
        next("Pacific Ocean"); // correct answer
        _lose("Atlantic Ocean");
        _lose("Indian Ocean");
        _lose("Arctic Ocean");
    }
}

@ question_10 {
    title   = "🍕 Question 10";
    message = "Which country is pizza originally from?";
    buttons {
        _lose("France");
        _end("Italy");          // correct answer
        _lose("Spain");
        _lose("USA");
    }
}

@ _lose {
    title   = "❌ Wrong Answer!";
    message = "Oops! {{random_lose_phrase}}";

    buttons {
        back("« Retry");
    }
}

@ _end {
    title   = "🎉 Quiz Complete!";
    message = "Congratulations! You've completed the Fun Facts Quiz! 🌟\n\nWant to try again?";

    buttons {
        main("↺ Restart Quiz");
    }
}

/* Suggested Emojis

↺ Restart
  What ？
✓ Okay

---

  Next »
« Back

---

  Next →
← Back

---

★ Starred
☆ Star

---

✓ Okay
✕ Cancel

---

⊕ Add
⊖ Remove

*/
"""
