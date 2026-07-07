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

import telekit

class HotelHandler(telekit.TelekitDSL.Mixin):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.message(commands=["hotel"]).invoke(cls.handle)
        cls.analyze_string(script)
        
    def handle(self):
        self.cart = []
        self.start_script()

    def add_to_cart(self, room_name: str):
        """API method called from DSL to add a room to the cart"""
        self.cart.append(room_name)

    def clear_cart(self):
        """API method called from DSL to clear the cart"""
        self.cart.clear()

    def get_variable(self, name: str) -> str | None:
        match name:
            case "cart_count":
                return str(len(self.cart))
            case "cart_list":
                return ", ".join(self.cart) if self.cart else "Your cart is empty"
            case "cart_v_list":
                return "\n".join(f"• {room}" for room in self.cart) if self.cart else "Your cart is empty"

# ------------------------------------------------------
# Telekit DSL
# ------------------------------------------------------
#
# Tutorial on GitHub: https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md
#

script = """
$ vars {
    ECONOM_PRICE = 50
    COMFORT_PRICE = 120
    NAME = ["Telekit", "Budapest", "Theft"]
}

@ main {
    title = "🏨 Grand {{random_NAME}} Hotel"
    message = "Welcome, {{first_name}}! Choose your experience and explore our rooms."
    
    buttons (2) {
        rooms("🛏️ Rooms")
        contact("📞 Contact")
    }
}

@ rooms {
    title = "🛏️ Rooms"
    message = "Select the type of room you'd like:"
    
    buttons (2) {
        econom("Economy Room")
        comfort("Comfort Room")
        back
    }
}

@ econom {
    title = "Economy Room"
    message = `
        A cozy and affordable room.
        
        Price: $ {{ECONOM_PRICE}} per night
    `
    image = "https://github.com/Romashkaa/images/blob/main/telekit_example_economy_room.png?raw=true"
    
    buttons (2) {
        back
        order("⊕ Add to Cart")
    }
}

@ comfort {
    title = "Comfort Room"
    message = `
        A spacious room with all modern amenities.
        
        Price: $ {{COMFORT_PRICE}} per night
    `
    image = "https://github.com/Romashkaa/images/blob/main/telekit_example_comfort_room.png?raw=true"
    
    buttons (2) {
        back
        order("⊕ Add to Cart")
    }
}

@ order {
    title = "✅ Added to Cart"
    message = "{{prev_scene_title}} added to your cart."
    
    buttons {
        cart("🛒 Go to Cart")
    }
    
    on_enter {
        add_to_cart("{{prev_scene_title}}")
    }
}

@ cart {
    title = "🛒 Rooms in your cart:"
    message = `
        _{{cart_v_list}}_
        
        Contact us to book these rooms: [Telegram](https://t.me/nottheromashka?text=Hello!%20I%20want%20to%20book%20these%20rooms:%20{{cart_list}})
    `
    parse_mode = "markdown"
    
    buttons (2) {
        cancel("✕ Cancel")
        rooms("Book more »")
    }
}

@ cancel {
    title = "🗑️ Cancel Booking"
    message = "Your current selection has been cleared."

    buttons {
        main("✓ Okay")
    }

    on_enter {
        clear_cart()
    }
}

@ contact {
    title = "📞 Contact"
    message = "You can reach us on Telegram: [Telekit Hotel](https://t.me/nottheromashka?text=Hello!%20I%20have%20a%20question%20about%20booking)"
    parse_mode = "markdown"
    
    buttons {
        back
    }
}
"""