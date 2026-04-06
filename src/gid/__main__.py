from gid.cli import argparser
from gid.parser import parse


def main() -> None:
    try:
        args = argparser.parse_args()
        parse(args)
    except Exception as e:
        print(f"An unknown error has occurred: {e}")


if __name__ == "__main__":
    main()
