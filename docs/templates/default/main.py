import telekit
import handlers

TOKEN: str = telekit.utils.read_token(".env")

telekit.Server(TOKEN).polling()