class TokenManager:
    """Class dealing with corporate withdrawal history"""

    def __init__(self, connection):
        self.connection = connection
        self.crypto_link = self.connection['CryptoLink']
        self.token_profiles = self.crypto_link.TokenProfiles

    def insert_new_token(self, data):
        result = self.token_profiles.insert_one(data)
        if result.inserted_id:
            return True
        else:
            return False
