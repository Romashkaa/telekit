import time

import telekit
from telekit.types import InlineKeyboard, Group
from telekit.traits import TrackHandoffOrigin

from telekit.styles import (
    # classic
    Bold, Italic, Underline, Strikethrough, Code, Python, Spoiler, Quote,
    Escape, Raw, Link, Mention, UserLink, BotLink, Stack,
    # rich: inline
    Marked, Subscript, Superscript, CustomEmoji, DateTime, Math, MathBlock,
    Anchor, AnchorLink, Reference,
    # rich: blocks
    Heading, Paragraph, Footer, Divider, Cite, PullQuote, Details,
    # rich: lists / tables
    ListItem, UnorderedList, OrderedList, Table, TableCell,
    # rich: media
    Image, Video, Audio, Map, Collage, Slideshow,
)


# ------------------------------------------------------------------
# Test assets (http/https only — Rich messages reject anything else)
# ------------------------------------------------------------------

IMG_1 = "https://picsum.photos/id/1015/800/500"
IMG_2 = "https://picsum.photos/id/1025/800/500"
IMG_3 = "https://picsum.photos/id/1035/800/500"
VIDEO = "https://www.w3schools.com/html/mov_bbb.mp4"
AUDIO = "https://www.w3schools.com/html/horse.ogg"


class RichTestHandler(TrackHandoffOrigin, telekit.Handler):
    """
    /rich — interactive test lab for Rich Messages (Rich HTML).

    Every page is rendered through the same pipeline
    (sender.set_rich_html(True) -> chain.edit()), so switching pages also tests
    editMessageText with `rich_message`.
    """

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("rich").invoke(cls.handle)

    # key -> button label. Order = order on the keyboard.
    SECTIONS: dict[str, list[tuple[str, str]]] = {
        "Styles": [
            ("inline", "Inline"),
            ("blocks", "Blocks"),
            ("lists", "Lists"),
            ("tables", "Tables"),
            ("math", "Math"),
            ("links", "Anchors & refs"),
            ("classic", "Classic styles"),
            ("newlines", "Newlines"),
        ],
        "Media": [
            ("media", "Image / Video / Audio"),
            ("collage", "Collage & Slideshow"),
            ("map", "Map"),
        ],
        "Sender": [
            ("photo_url", "Photo URL"),
            ("photo_group", "Photo group"),
            ("ignored", "Ignored attachments"),
            ("preview", "Link preview"),
            ("rtl", "RTL"),
            ("no_entities", "Skip entity detect."),
        ],
        "Fallback": [
            ("downgrade", "Downgrade to HTML"),
            ("markdown", "Markdown mode"),
            ("raw_html", "Raw rich HTML"),
            ("escape", "Escaping"),
        ],
        "Edge cases": [
            ("bad_src", "Invalid media src"),
            ("too_long", "Too long"),
            ("empty", "Empty text"),
            ("big_table", "Big combined"),
        ],
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.current: str = "menu"

    # ------------------------------------------------------------------
    # Entry
    # ------------------------------------------------------------------

    def handle(self) -> None:
        self.menu()

    def menu(self) -> None:
        self.show("menu")

    # ------------------------------------------------------------------
    # Core renderer
    # ------------------------------------------------------------------

    def show(self, key: str) -> None:
        self.current = key
        sender = self.chain.sender

        self._reset_sender()
        sender.set_rich_html(True)  # pages may override this

        try:
            text = getattr(self, f"page_{key}")()
        except Exception as exception:  # building the page itself failed
            text = Group(Bold("❌ Page builder failed"), "\n", Code(repr(exception)))
            sender.set_rich_html(False)

        sender.set_text(text)
        self.chain.set_keyboard(self._keyboard(key))

        try:
            self.chain.edit()
        except Exception as exception:
            # e.g. RichMessageError (a ValueError subclass), Telegram API errors
            self._show_error(key, exception)

    def _show_error(self, key: str, exception: Exception) -> None:
        sender = self.chain.sender
        self._reset_sender()
        sender.set_rich_html(False)
        sender.set_text(
            Group(
                Bold(f"❌ Page «{key}» failed"), "\n\n",
                Bold(type(exception).__name__), "\n",
                Code(str(exception)[:500]), "\n\n",
                Italic("This may be the expected result for edge-case pages."),
            )
        )
        self.chain.set_keyboard(self._keyboard("error"))
        self.chain.edit()

    def _reset_sender(self) -> None:
        """Clears state that earlier pages could leave on the (reused) sender."""
        sender = self.chain.sender
        sender.photo = None
        sender.media = []
        sender.document = None
        sender.link_preview_options = None
        sender._rich_is_rtl = None                  # internal attrs, see _rich_message_json
        sender._rich_skip_entity_detection = None

    def _keyboard(self, key: str) -> InlineKeyboard:
        keyboard = InlineKeyboard()

        if key == "menu":
            for section, pages in self.SECTIONS.items():
                keyboard = keyboard.grid(2)
                for page_key, label in pages:
                    keyboard = keyboard.add_callback(label, self.show, [page_key])
                keyboard = keyboard.grid_end()
            return keyboard.add_callback("« Back", self.handoff_back, when=self.is_handed_off)

        return (
            keyboard
            .grid(2)
                .add_callback("« Menu", self.menu)
                # .add_callback("↻ Reload", self.show, [self.current])
            .grid_end()
        )

    # ==================================================================
    # PAGES — Menu
    # ==================================================================

    def page_menu(self):
        return Group(
            Heading("🧪 Rich Messages test lab", level=2),
            Paragraph("Pick a page. Each one exercises a part of the rich pipeline."),
            UnorderedList(
                Group(Bold("Styles"), " — every rich entity"),
                Group(Bold("Media"), " — image, video, audio, map, collage"),
                Group(Bold("Sender"), " — photo/attachments/link preview rules"),
                Group(Bold("Fallback"), " — downgrade, markdown, escaping"),
                Group(Bold("Edge cases"), " — errors and warnings"),
            ),
            Footer("Watch the console for library warnings."),
        )

    # ==================================================================
    # PAGES — Styles
    # ==================================================================

    def page_inline(self):
        unix = int(time.time()) + 86400
        return Group(
            Heading("Inline styles", level=3),
            Paragraph(
                Bold("bold"), ", ", Italic("italic"), ", ", Underline("underline"), ", ",
                Strikethrough("strike"), ", ", Spoiler("spoiler"), ", ",
                Code("code"), ", ", Marked("marked"),
            ),
            Paragraph(
                "H", Subscript("2"), "O  ·  x", Superscript("2"), " + y", Superscript("3"),
            ),
            Paragraph(
                "Custom emoji: ", CustomEmoji("👍", emoji_id=5368324170671202286),
            ),
            Paragraph(Bold("Nested: "), Marked(Bold(Italic("marked bold italic")))),
            Heading("Date & time", level=4),
            UnorderedList(
                Group("default: ", DateTime("tomorrow", unix=unix)),
                Group("wDT: ", DateTime("tomorrow", unix=unix, format="wDT")),
                Group("relative (r): ", DateTime("tomorrow", unix=unix, format="r")),
                Group("time only (t): ", DateTime("tomorrow", unix=unix, format="t")),
                Group("date only (d): ", DateTime("tomorrow", unix=unix, format="d")),
            ),
            Python("print('rich + code')"),
        )

    def page_blocks(self):
        return Group(
            Heading("Heading level 1", level=1),
            Heading("Heading level 2", level=2),
            Heading("Heading level 3", level=3),
            Heading("Heading level 4", level=4),
            Heading("Heading level 5", level=5),
            Heading("Heading level 6", level=6),
            Paragraph("A paragraph of text. ", Bold("Bold"), " inside."),
            Paragraph("A second paragraph — separated from the first."),
            Divider(),
            Quote("Regular quote.", Cite("— Someone Wise")),
            Quote("Expandable quote. " * 12, expandable=True),
            PullQuote("Pull quote: big and centered.", credit="Author Name"),
            Details(
                "Hidden content, ", Bold("revealed!"),
                summary="Click to expand (closed)",
            ),
            Details(
                "This one starts open.",
                Details("Nested details inside.", summary="Nested"),
                summary="Click to collapse (open)",
                is_open=True,
            ),
            Divider(),
            Footer("This is a footer"),
        )

    def page_lists(self):
        return Group(
            Heading("Lists", level=3),
            Paragraph(Bold("Unordered")),
            UnorderedList("One", Bold("Two (bold)"), ListItem("Three (ListItem)")),
            Paragraph(Bold("Ordered")),
            OrderedList("First", "Second", "Third"),
            Paragraph(Bold("Ordered, start=5, type=a")),
            OrderedList("Five", "Six", "Seven", start=5, type="a"),
            Paragraph(Bold("Ordered, type=I")),
            OrderedList("Alpha", "Beta", "Gamma", type="I"),
            Paragraph(Bold("Ordered, reversed")),
            OrderedList("Three", "Two", "One", reversed=True),
            Paragraph(Bold("Explicit ListItem value")),
            OrderedList(ListItem("ten", value=10), ListItem("twenty", value=20), "next"),
            Paragraph(Bold("Nested")),
            UnorderedList(
                ListItem("Parent A", UnorderedList("child a1", "child a2")),
                ListItem("Parent B", OrderedList("child b1", "child b2")),
            ),
        )

    def page_tables(self):
        return Group(
            Heading("Tables", level=3),
            Table(
                ["Name", "Score", "Status"],
                ["Ann", "10", Bold("passed")],
                ["Bob", "7", Italic("retry")],
                ["Cid", "3", Strikethrough("failed")],
                header=True, bordered=True, caption="Header + bordered",
            ),
            Table(
                ["#", "Value"],
                ["1", "alpha"], ["2", "beta"], ["3", "gamma"], ["4", "delta"],
                header=True, striped=True, caption="Striped",
            ),
            Table(
                [TableCell("Merged header", header=True, colspan=3, align="center")],
                [
                    TableCell("left", align="left"),
                    TableCell("center", align="center"),
                    TableCell("right", align="right"),
                ],
                [
                    TableCell("rowspan", rowspan=2, valign="middle"),
                    "b", "c",
                ],
                ["d", "e"],
                bordered=True, caption="colspan / rowspan / align",
            ),
        )

    def page_math(self):
        return Group(
            Heading("Math", level=3),
            Paragraph("Inline: ", Math(r"E = mc^2"), " and ", Math(r"a^2 + b^2 = c^2")),
            Paragraph("Block formula:"),
            MathBlock(r"\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}"),
            MathBlock(r"\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}"),
            Paragraph("Special chars must survive: ", Math(r"a < b \land c > d")),
        )

    def page_links(self):
        return Group(
            Anchor("top"),
            Heading("Anchors & references", level=3),
            Paragraph(
                "Footnote reference", AnchorLink("[1]", name="fn1"),
                " and another", AnchorLink("[2]", name="fn2"), ".",
            ),
            Paragraph(AnchorLink("↓ jump to bottom", name="bottom")),
            Paragraph("Filler. " * 80),
            Divider(),
            Reference("First footnote text.", name="fn1"),
            Reference("Second footnote text.", name="fn2"),
            Anchor("bottom"),
            Paragraph(AnchorLink("↑ back to top (empty name)")),
            Paragraph(AnchorLink("↑ back to top (named)", name="top")),
        )

    def page_classic(self):
        return Group(
            Heading("Classic styles inside rich", level=3),
            Paragraph(
                Link("Link", url="https://github.com/Romashkaa/telekit"), " · ",
                Mention("Mention", user_id=self.user.id), " · ",
                UserLink("UserLink", username="durov", text="Hi!"), " · ",
                BotLink("BotLink", username="BotFather", start="test"),
            ),
            Stack("Stack item one", "Stack item two", "Stack item three"),
            Stack("Dot", "Dot", start=Stack.Markers.DOT),
            Stack("Check", "Check", start=Stack.Markers.CHECK, end="."),
            Python("def hello():\n    return 'rich'\n"),
            Quote("Classic blockquote"),
        )

    def page_newlines(self):
        return Group(
            Heading("Newline handling", level=3),
            "Line 1\nLine 2\nLine 3  (plain \\n -> <br/>)\n\n",
            Bold("Bold\nacross\nlines"), "\n",
            Stack("Stack A", "Stack B", "Stack C"),
            "Text right after Stack\n",
            Quote("Quote line 1\nQuote line 2"),
            "Text right after Quote\n",
            Python("a = 1\nb = 2\nprint(a + b)"),
            "Text right after code block\n\n\n",
            "Three newlines above should not explode into huge gaps.",
        )

    # ==================================================================
    # PAGES — Media
    # ==================================================================

    def page_media(self):
        return Group(
            Heading("Single media blocks", level=3),
            Image(IMG_1),
            Image(IMG_2, caption="Caption only"),
            Image(IMG_3, caption="Caption + credit", credit="Photo: picsum.photos"),
            Image(IMG_1, caption="Spoiler image", spoiler=True),
            Video(VIDEO, caption="Video block"),
            Audio(AUDIO, caption="Audio block (.ogg is a voice note)"),
        )

    def page_collage(self):
        return Group(
            Heading("Collage", level=3),
            Collage(Image(IMG_1), Image(IMG_2), Image(IMG_3)),
            Heading("Slideshow", level=3),
            Slideshow(Image(IMG_1, caption="One"), Image(IMG_2, caption="Two"), Image(IMG_3, caption="Three")),
        )

    def page_map(self):
        return Group(
            Heading("Maps", level=3),
            Paragraph("Zoom 13 (min):"),
            Map(50.4501, 30.5234, zoom=13),
            Paragraph("Zoom 15 (default):"),
            Map(50.4501, 30.5234),
            Paragraph("Zoom 20 (max):"),
            Map(50.4501, 30.5234, zoom=20),
        )

    # ==================================================================
    # PAGES — Sender integration
    # ==================================================================

    def page_photo_url(self):
        """URL photo is embedded into the rich text (self.text untouched)."""
        self.chain.sender.photo = IMG_1
        return Group(
            Heading("Photo from URL", level=3),
            Paragraph("The photo above is embedded before this text (show_caption_above_media=False)."),
        )

    def page_photo_group(self):
        """Several URL photos in a media group -> collage."""
        from telebot.types import InputMediaPhoto

        self.chain.sender.media = [InputMediaPhoto(url) for url in (IMG_1, IMG_2, IMG_3)]
        return Group(
            Heading("Media group -> collage", level=3),
            Paragraph("Three URL photos should be rendered as a collage."),
        )

    def page_ignored(self):
        """Local photo / document -> ignored with a console warning."""
        self.chain.sender.photo = "local_photo.jpg"     # not a URL
        self.chain.sender.document = "report.pdf"       # unsupported in rich
        return Group(
            Heading("Ignored attachments", level=3),
            Paragraph("Local photo and document must be ignored."),
            Footer("Console: «Rich messages do not support these attachments»"),
        )

    def page_preview(self):
        self.chain.sender.set_link_preview_options(show_above_text=True)
        return Group(
            Heading("Link preview", level=3),
            Paragraph(
                "No preview card should appear for ",
                Link("this link", url="https://en.wikipedia.org/wiki/Mariana_Trench"),
                ". Console: «link_preview_options is not supported».",
            ),
        )

    def page_rtl(self):
        self.chain.sender._rich_is_rtl = True
        return Group(
            Heading("RTL layout", level=3),
            Paragraph("مرحبا بالعالم — هذه فقرة تجريبية من اليمين إلى اليسار."),
            UnorderedList("بند أول", "بند ثان"),
        )

    def page_no_entities(self):
        self.chain.sender._rich_skip_entity_detection = True
        return Group(
            Heading("skip_entity_detection=True", level=3),
            Paragraph("These must stay plain text (no auto-links):"),
            Paragraph("https://example.com  @username  #hashtag  +380501234567"),
        )

    # ==================================================================
    # PAGES — Fallback
    # ==================================================================

    def _kitchen_sink(self):
        return Group(
            Heading("Kitchen sink", level=2),
            Paragraph("Para with ", Bold("bold"), ", ", Marked("marked"), ", H", Subscript("2"), "O, x", Superscript("2"), "."),
            Divider(),
            UnorderedList("bullet one", "bullet two"),
            OrderedList("num one", "num two", start=3),
            Table(["A", "B"], ["1", "2"], ["3", "4"], header=True, caption="Table"),
            Quote("Quote"),
            PullQuote("Pull", credit="Credit"),
            Details("Hidden", summary="Details"),
            MathBlock(r"x^2"),
            Math(r"y"),
            Footer("Footer"),
            Image(IMG_1, caption="Dropped when downgraded"),
            Map(50.4501, 30.5234),
        )

    def page_downgrade(self):
        """rich_html OFF + rich tags in html parse_mode -> downgrade_rich_html()."""
        self.chain.sender.set_rich_html(False)
        self.chain.sender.set_parse_mode("html")
        return Group(
            Italic("(rich mode OFF — regular message with downgraded tags)"), "\n",
            self._kitchen_sink(),
        )

    def page_markdown(self):
        """Rich entities rendered in markdown mode."""
        self.chain.sender.set_rich_html(False)
        self.chain.sender.set_parse_mode("markdown")
        return Group(
            Heading("Markdown fallback", level=2),
            Paragraph("Para ", Bold("bold"), " ", Italic("italic")),
            Divider(),
            UnorderedList("one", "two"),
            OrderedList("one", "two"),
            Table(["A", "B"], ["1", "2"], header=True),
        )

    def page_raw_html(self):
        """Hand-written rich HTML passed through Raw()."""
        return Raw(
            "<h2>Raw rich HTML</h2>"
            "<p>Hand-written <b>bold</b>, <mark>mark</mark>, <sub>sub</sub>, <sup>sup</sup>.</p>"
            "<hr/>"
            "<ul><li>raw one</li><li>raw <i>two</i></li></ul>"
            "<table bordered><tr><th>H1</th><th>H2</th></tr><tr><td>a</td><td>b</td></tr></table>"
            "<details><summary>Raw details</summary>hidden</details>"
            "<blockquote>Raw quote</blockquote>"
            "<pre language=\"python\">print('raw')</pre>"
            "<p>Line with<br/>manual break</p>"
        )

    def page_escape(self):
        evil = "<b>not bold</b> & <h1>not a heading</h1> <script>alert(1)</script> 5 < 6 > 4"
        return Group(
            Heading("Escaping", level=3),
            Paragraph(Bold("Plain string (auto-escaped):")),
            Paragraph(evil),
            Paragraph(Bold("Escape():")),
            Paragraph(Escape(evil)),
            Paragraph(Bold("Bold(escape=False) — tags interpreted:")),
            Paragraph(Bold("<i>interpreted italic</i>", escape=False)),
            Paragraph(Bold("Raw():")),
            Raw("<p><u>raw underline</u></p>"),
            Paragraph(Bold("Link with quotes in label:"), " ", Link('say "hi" & <bye>', url="https://example.com/?a=1&b=2")),
            Paragraph(Bold("Math keeps symbols:"), " ", Math(r"a < b")),
        )

    # ==================================================================
    # PAGES — Edge cases
    # ==================================================================

    def page_bad_src(self):
        """Non http(s)/tg media src -> warning."""
        return Raw(
            "<p>Invalid sources (see console):</p>"
            "<img src=\"ftp://example.com/a.jpg\"/>"
            "<img src=\"/local/path.png\"/>"
            "<video src=\"file:///video.mp4\"></video>"
        )

    def page_too_long(self):
        """> RICH_MAX_LENGTH (32768) -> warning, Telegram may reject."""
        return Group(Heading("Too long", level=3), Paragraph("x" * 33_000))

    def page_empty(self):
        """Empty text -> RichMessageError (shown on the error page)."""
        return ""

    def page_big_table(self):
        """Stress: many rows + all inline styles inside cells."""
        rows: list = [["#", "Bold", "Italic", "Code", "Marked"]]
        for i in range(1, 21):
            rows.append([str(i), Bold(f"b{i}"), Italic(f"i{i}"), Code(f"c{i}"), Marked(f"m{i}")])
        return Group(
            Heading("Stress test", level=3),
            Table(*rows, header=True, bordered=True, striped=True, caption="20 rows × 5 cols"),
            Details(self._kitchen_sink(), summary="Everything inside Details", is_open=True),
        )