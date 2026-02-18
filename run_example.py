import telekit

with open("token.txt") as f:
    TOKEN: str = f.readline().strip()

telekit.example(TOKEN)