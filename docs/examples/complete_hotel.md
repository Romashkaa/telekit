# Complete Hotel Example

> `main.py` file:

```py
import telekit

class CompleteHotelHandler(telekit.TelekitDSL.Mixin):

    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_file("script.scr")
        cls.on.command("start").invoke(cls.start_script)

telekit.Server(TOKEN).polling()
```

> `script.scr` file:

```go
@ main {
    title = "👋 Welcome to the Hotel Ukraine"
    message = `
        Here you can:
        • check available rooms
        • get important information about your stay

        Use the buttons below to get started:
    `
    image = "https://kyiv24.news/wp-content/uploads/2024/09/gotel-ukra.jpg"
    buttons (2) {
        overview("🌟 Overview")
        rooms("🛏️ Rooms")
        faq("ℹ️ FAQ")
    }
}

// ------------------------------------------------------------------
// Rooms
// ------------------------------------------------------------------

@ rooms {
    title = "🛏️ Rooms"
    message = `
        Hotel Ukraine has 363 rooms. The modern rooms are equipped with everything necessary for guests’ comfort and relaxation. Complimentary wireless Internet (Wi-Fi) is available in the rooms and public areas of the hotel.

        Please select the type of room you'd like:
    `
    image = "https://ukraine-hotel.s3.amazonaws.com/uploadimage/01f45b301b334c65bd0978fc020b98bf.jpg"
    
    buttons {
        standard_room("Maydan View – Standard")
        comfort_room("Executive Suite – Comfort")
        premium_room("Business Suite – Premium")
        back()
    }
}

@ standard_room {
    title = "Maydan View – Standard"
    message = `
        A one-room panoramic suite with a view of Kyiv’s central square – Maidan Nezalezhnosti. The room includes: comfortable furniture, a large double bed or two single beds, a bathroom with modern amenities, air conditioning, a safe, a refrigerator, and complimentary toiletries.

        • Stars: ★★★☆☆
        • Capacity: 2 adults
        • Room size: 35 m²
        • Rent: 2975 UAH per night
    `
    parse_mode = "markdown"
    image = "https://ukraine-hotel.s3.amazonaws.com/uploadimage/fb52f495c15d42ac89fe9552fa83640f.jpg"
    
    buttons (3) {
        back("« Menu")
        link("Book", "https://t.me/NotTheRomashka?text=Hello!%20I%20would%20like%20to%20book%20a%20room.%20Please%20provide%20availability%20and%20pricing%20details.")
        next()
    }
}

@ comfort_room {
    title = "Executive Suite – Comfort"
    message = `
        An exclusive suite with panoramic views of Maidan Nezalezhnosti. The suite features two bedrooms, two bathrooms, and a spacious living room with a sofa and comfortable armchairs.

        • Stars: ★★★★☆
        • Capacity: 4 adults
        • Room size: 76 m²
        • Rent: 5015 UAH per night
    `
    parse_mode = "markdown"
    image = "https://ukraine-hotel.s3.amazonaws.com/uploadimage/09fcaf94d3ce4076bd808546cc8c20be.jpg"
    
    buttons (3) {
        back("« Previous")
        link("Book", "https://t.me/NotTheRomashka?text=Hello!%20I%20would%20like%20to%20book%20a%20room.%20Please%20provide%20availability%20and%20pricing%20details.")
        next()
    }
}

@ premium_room {
    title = "Business Suite – Premium"
    message = `
        A three-room suite with panoramic views of Maidan Nezalezhnosti. The suite includes: a bedroom with a king-size bed, a study with a desk and chair, and a cozy living room.

        • Stars: ★★★★★
        • Capacity: 3 adults
        • Room size: 50 m²
        • Rent: 5015 UAH per night
    `
    image = "https://ukraine-hotel.s3.amazonaws.com/uploadimage/7478f00bc9684595ad6de1b564c714f3.jpg"
    parse_mode = "markdown"

    buttons (3) {
        back("« Previous")
        link("Book", "https://t.me/NotTheRomashka?text=Hello!%20I%20would%20like%20to%20book%20a%20room.%20Please%20provide%20availability%20and%20pricing%20details.")
        return("Menu ↺", "rooms")
    }
}

// ------------------------------------------------------------------
// Contact
// ------------------------------------------------------------------

@ contact {
    title = "ℹ️ Contact"
    message = `
        📞 Phone – +380952860143
        
        📬 Mail – http://ukraine-hotel.kiev.ua/
        
        📍 Address – [Alley of Heroes of the Heavenly Hundred, Kyiv, Ukraine](https://maps.app.goo.gl/SPLuWbzdUdigYqMV7)
    `
    parse_mode = "markdown"
    image = "https://minio.kyivcity.gov.ua/portal-guide/places/TKsqHryfHNLeY5s9RwVguOzJmbneb4KXVcH2Q1be.jpeg"
    
    buttons (2) {
        back()
        link("Support", "https://t.me/NotTheRomashka?text=Hello!%20I%20have%20a%20question%20about%20booking")
    }
}

// ------------------------------------------------------------------
// FAQ
// ------------------------------------------------------------------

@ faq {
    title = "📖 FAQ – Hotel Ukraine"
    message = `
        *Is Wi-Fi available at the hotel?*
        • _Yes, free Wi-Fi is available throughout the hotel._

        *Is breakfast included?*
        • _Breakfast is available for an additional fee._

        *Is parking available on site?*
        • _Yes, paid parking is available for guests._

        *Is the hotel accessible for guests with disabilities?*
        • _Yes._

        *Does the hotel have air conditioning?*
        • _Yes, all rooms are equipped with air conditioning._

        *Are pets allowed?*
        • _Yes, pets are allowed._

        *Does the hotel have a restaurant and bar?*
        • _Yes, Hotel Ukraine features a restaurant and a bar._

        *Are there fitness or business facilities?*
        • _Yes, the hotel offers a fitness center and a business center._

        *Is airport transportation available?*
        • _Yes, airport shuttle service is available upon request._
    `
    parse_mode = "markdown"
    image = "https://cf.bstatic.com/xdata/images/hotel/max1024x768/735063748.jpg?k=30f7a9d5f4d5fc7f168f50aa1d752b87f2e28e83641bc6471b543ab3803d86df&o="

    buttons (2) {
        back()
        contact("Contact")
    }
}

// ------------------------------------------------------------------
// Overview
// ------------------------------------------------------------------

@ overview {
    title = "⚜️ About Hotel Ukraine"
    message = `
        This classically styled hotel is located in a grand building, just a 6-minute walk from the central Independence Square (Maidan Nezalezhnosti) and 1 km from Saint Sophia Cathedral.

        The comfortably furnished rooms offer Wi-Fi access and cable TV. Suite rooms feature separate living areas, and some of them provide panoramic city views.

        Breakfast is available. Guests can enjoy a sauna, a beauty salon, and an elegant restaurant with two dining halls. Parking facilities are also available.
    `
    image = "https://i.obozrevatel.com/news/2024/12/16/filestorage5temp.jpeg?size=972x462"
    buttons (2) {
        back()
        faq("FAQ")
    }
}
```