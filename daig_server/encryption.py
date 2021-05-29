from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_OAEP
import os

package_directory = os.path.dirname(os.path.abspath(__file__))
encrypted_dir=os.path.join(package_directory,"encrypted_data")

def load_encrypted_data(data_path, key_path):

    with open(key_path,"r", encoding="utf-8") as f:
        private_key = RSA.import_key(f.read())

    with open(data_path, "rb") as f:
        enc_session_key, nonce, tag, ciphertext = \
            [ f.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data.decode()

def get_email():
    key_path=os.path.join(encrypted_dir,"private.pem")
    data_path=os.path.join(encrypted_dir,"encrypted_email.bin")
    return load_encrypted_data(data_path, key_path)

def get_password():
    key_path=os.path.join(encrypted_dir,"private.pem")
    data_path=os.path.join(encrypted_dir,"encrypted_pwd.bin")
    return load_encrypted_data(data_path, key_path)