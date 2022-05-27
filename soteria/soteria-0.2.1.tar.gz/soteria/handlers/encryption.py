import yaml
import sys
import base64


class Encryption:

    def __init__(self):

        self.decrypted_values = {}

    def reload_values(self):

        # Load YAML file
        encrypted_values = self.load_yaml()

        # Check for any non-encrypted values, if any found, encrypt them
        if encrypted_values:
            for key in encrypted_values:
                encrypted = encrypted_values[key]

                if type(encrypted) == str:
                    encrypted = self.encrypt_value(encrypted)
                    encrypted_values[key] = encrypted

                self.decrypted_values[key] = self.decrypt_value(encrypted)

            # Save back to file
            self.save_to_file(encrypted_values)

    def encrypt_value(self, value):

        encrypted = base64.urlsafe_b64encode(value.encode("utf-8"))

        return encrypted

    def decrypt_value(self, value):

        return base64.urlsafe_b64decode(value).decode("utf-8")

    def save_to_file(self, values):

        with open('encrypted.yaml', 'w') as f:
            yaml.dump(values, f, width=2000)

    def load_yaml(self):

        try:
            with open('encrypted.yaml', 'r') as stream:
                return yaml.safe_load(stream)
        except FileNotFoundError:
            sys.exit('encrypted.yaml file not found')

    def get_value(self, key):

        self.reload_values()

        try:
            decrypted_value = self.decrypted_values[key]
        except KeyError:
            decrypted_value = 'Key not found in encryption.yaml'

        return decrypted_value
