import telekit
from telekit.traits import PaginatedText

ARTICLE = """
The internet began as <b>ARPANET</b> in the late 1960s, a US military research \
network designed to survive a nuclear attack by routing packets around damaged nodes. \
<i>It was never meant to become what it is today.</i>

<b>1970s — Protocols are born</b>

Vint Cerf and Bob Kahn designed <b>TCP/IP</b> in 1974 — the foundational protocol \
that made it possible for different networks to speak to each other. Without it, \
every network would have remained an isolated island. ARPANET officially switched \
to TCP/IP on <i>January 1, 1983</i>, a date sometimes called the "birthday of the internet".

<b>1980s — The net goes academic</b>

NSFNet replaced ARPANET as the backbone, connecting universities across the US \
and eventually the world. Email became the killer app of the decade. <b>Domain names</b> \
were introduced in 1985 so humans wouldn't have to memorise raw IP addresses.

<b>1990s — The Web changes everything</b>

Tim Berners-Lee invented the <b>World Wide Web</b> at CERN in 1989 and published \
it in 1991. Suddenly the internet had a face. Mosaic (1993) was the first browser \
ordinary people could use. By the end of the decade, companies like Amazon, Google, \
and eBay had launched — and the dot-com bubble was in full swing.

<b>2000s — Broadband and social media</b>

Dial-up gave way to always-on broadband. <b>Wikipedia</b> launched in 2001. \
<b>Facebook</b> in 2004, <b>YouTube</b> in 2005, <b>Twitter</b> in 2006. \
The web stopped being something you visited and became something you lived in.

<b>2010s — Mobile first</b>

The smartphone put the internet in every pocket. By 2016 mobile traffic surpassed \
desktop for the first time. <i>The cloud</i> moved computing off local machines. \
Streaming killed packaged media. End-to-end encryption moved from niche to mainstream.

<b>2020s — AI and what comes next</b>

Large language models, diffusion image generators, and real-time translation are \
reshaping how people interact with information. The internet is no longer just a \
network of documents — it is becoming a layer of machine intelligence woven into \
everyday life.
""".strip()

class ArticleHandler(PaginatedText, telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("article").invoke(cls.handle)

    def handle(self) -> None:
        self.chain.sender.set_photo("https://png.pngtree.com/png-clipart/20250513/original/pngtree-blue-globe-internet-icon-representing-worldwide-web-browser-global-network-png-image_20954600.png")
        self.chain.sender.set_title("🌍 The History of the Internet")
        self.chain.sender.set_remove_text(False)
        self.chain.sender.set_remove_attachments(False)

        self.paginated_text(
            ARTICLE, 
            chunk=210, 
            window=10,
            show_ellipsis=True
        )