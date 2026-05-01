import telekit

TOKEN: str = telekit.utils.read_token(".env")

telekit.example(TOKEN)


