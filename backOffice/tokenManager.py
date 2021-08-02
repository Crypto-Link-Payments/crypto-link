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

    def check_token_existence(self, issuer, code):
        result = self.token_profiles.find_one({"assetIssuer": issuer, "assetCode": code})
        if result:
            return True
        else:
            return False

    def get_token_details_by_code(self, code):
        return self.token_profiles.find_one({"assetCode": code})

    def get_token_details_by_issuer(self, issuer, code):
        return self.token_profiles.find_one({"assetIssuer": issuer, "assetCode": code},
                                            {"_id"})

    def update_token_profile(self, issuer, code, data: dict):
        result = self.token_profiles.update_one({"assetIssuer": issuer, "assetCode": code},
                                                {"$set", data})
        return result.matched_count > 0

    def get_registered_tokens(self):
        result = list(self.token_profiles.find({},
                                               {"_id": 0,
                                                "assetCode": 1}))
        return result

    def get_all_tokens(self):
        return list(self.token_profiles.find({}))
