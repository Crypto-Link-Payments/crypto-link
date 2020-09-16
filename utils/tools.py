import json
import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

class Helpers():
    def __init__(self):
        pass

    def read_json_file(self, file_name: str):
        """
        Loads the last block height which was stored in last_block.json
        :return: Block height as INT
        """

        # Reads last marked block data in the document
        path = f'{project_path}/{file_name}'
        try:
            with open(path) as json_file:
                data = json.load(json_file)
                return data
        except IOError:
            return None

    def update_json_file(self, file_name: str, key, value):
        """
        Stores the height of last block which was monitored for incoming transactions
        :param block_height: block height from RPC Daemon as INT
        :return: Updates the value in last_block.json
        """
        try:
            # read data
            data = self.read_json_file(file_name)
            data[key] = value
            path = f'{project_path}/{file_name}'
            with open(path, 'w') as f:
                json.dump(data, f)
            return True
        except Exception:
            return False