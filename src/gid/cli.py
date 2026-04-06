import argparse

argparser = argparse.ArgumentParser(description="A git index file parser.")

argparser.add_argument(
    "-i",
    "--input",
    metavar="FILEPATH",
    default="./git/index",
    type=str,
    help="The filepath of the git index file.",
)

argparser.add_argument(
    "-q",
    "--quiet",
    action="store_true",
    help="Suppress all output except errors.",
)

argparser.add_argument(
    "--to-json",
    metavar="FILEPATH",
    type=str,
    help="Export the results to the specified JSON file path.",
)
