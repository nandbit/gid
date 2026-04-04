import argparse


def setup_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="A git index file parser.")

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress all output except errors.",
    )

    parser.add_argument(
        "--to-json",
        metavar="FILEPATH",
        type=str,
        help="Export the results to the specified JSON file path.",
    )

    return parser
