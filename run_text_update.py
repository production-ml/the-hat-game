from datetime import datetime, timedelta
from time import sleep

from server.data import add_new_text


def main():

    while True:
        add_new_text()
        now = datetime.utcnow
        to = (now() + timedelta(days=1)).replace(hour=1, minute=0, second=0)
        sleep((to - now()).seconds)


if __name__ == "__main__":
    main()
