def strike(text: str):
    result = ""
    for character in text:
        result += character + '\u0336'
    return result
