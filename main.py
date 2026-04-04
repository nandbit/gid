from gid.argparse import setup_argparser
from gid.decoder import decode


def main():
    index_filepath = "./tests/01.index"
    argparser = setup_argparser()
    decode(
        index_filepath,
        argparser.parse_args(),
    )


if __name__ == "__main__":
    main()
