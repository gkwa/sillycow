import argparse

from . import main2

__project_name__ = "sillycow"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare .tfvars files in a directory."
    )
    parser.add_argument(
        "--basedir",
        type=str,
        default=".",
        help="Base directory to search for .tfvars files",
    )
    args = parser.parse_args()
    code = main2.compare_tfvars_files(args.basedir)
    return code
