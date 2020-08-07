import base64
import uuid

class TokenGenerator:
    token_code = ''
    url_token = ''
    token = ''

    def __init__(self):
        TokenGenerator.generate_token(self)

    def generate_token(self):
        random_id_1 = str(uuid.uuid4())
        random_id_2 = str(uuid.uuid4())
        random_id_3 = str(uuid.uuid4())

        self.token_code = random_id_1 + '-' + random_id_2 + '-' + random_id_3
        bytes_code = self.token_code.encode('utf-8')
        bytes_token = base64.urlsafe_b64encode(bytes_code)
        self.url_token = bytes_token.decode()

    @classmethod
    def decode_token(cls, received_token):
        decoded_token = base64.urlsafe_b64decode(received_token)
        cls.token = decoded_token.decode()
