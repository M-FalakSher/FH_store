import bcrypt

# The password we want to use
password = "admin123"

# Generate the hash
# bcrypt requires bytes, so we encode the string
bytes = password.encode('utf-8')
salt = bcrypt.gensalt()
hash_password = bcrypt.hashpw(bytes, salt)

print("\n--- COPY THIS HASH BELOW ---")
print(hash_password.decode('utf-8'))
print("--- END OF HASH ---\n")