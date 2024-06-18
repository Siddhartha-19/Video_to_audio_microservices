import secrets

def generate_secret_key():
    return secrets.token_hex(32)  

print(generate_secret_key())