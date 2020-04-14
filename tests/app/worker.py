from liteblue import worker
from .main import Docker


def main():
    worker.main(Docker)


if __name__ == '__main__':
    main()
