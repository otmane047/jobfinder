from config import Config


def vigenere_encryption(message,user):
    key = Config.SECRET_KEY.lower() + user.lower()
    encrypted_message = str()
    key_index = 0
    for char in message.lower():
        if char.isalpha():
            shift = ord(key[key_index]) - ord('a')
            encrypted_char = chr(((ord(char) - ord('a') + shift) % 26) + ord('a'))
            encrypted_message += encrypted_char
            key_index = (key_index + 1) % len(key)
        else:
            encrypted_message += char
    return encrypted_message


def vigenere_decryption(encrypted_message,user):
    key = Config.SECRET_KEY.lower() + user.lower()
    decrypted_message = ""
    key_index = 0
    for char in encrypted_message.lower():
        if char.isalpha():
            shift = ord(key[key_index]) - ord('a')
            decrypted_char = chr(((ord(char) - ord('a') - shift + 26) % 26) + ord('a'))
            decrypted_message += decrypted_char
            key_index = (key_index + 1) % len(key)
        else:
            decrypted_message += char
    return decrypted_message