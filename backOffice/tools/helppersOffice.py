from uuid import uuid4


class VariousTools(object):
    def __main__(self):
        pass

    @staticmethod
    def get_xlm_payment_id():
        """
        Create user memo when wallet is created for deposits
        :return: STR
        """
        string_length = 20
        random_string = uuid4().hex  # get a random string in a UUID fromat
        memo = random_string.upper().lower()[0:string_length]
        return str(memo)
