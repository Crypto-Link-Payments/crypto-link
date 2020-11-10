from stellar_sdk import Server


class HorizonServer:
    def __init__(self):
        self.server = Server(horizon_url="https://horizon-testnet.stellar.org")


server = HorizonServer().server
