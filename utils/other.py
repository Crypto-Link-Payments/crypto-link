from datetime import datetime

def from_unix(unix):
    time = datetime.utcfromtimestamp(unix)
    return time


