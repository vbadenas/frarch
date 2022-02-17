import argparse
from pathlib import Path
from typing import Any, Dict, Tuple


def parse_arguments() -> Tuple[str, Dict[str, Any]]:
    """Parse arguments from command line.

    Returns:
        params_file (str): hyperparams file path.
        args (Dict[str, Any]]): arguments from argparse.Namespace.
    """
    parser = argparse.ArgumentParser(
        description="Run an experiment",
    )
    parser.add_argument(
        "param_file",
        type=str,
        help="A yaml-formatted file using the extended YAML syntax. "
        "defined by HyperPyYaml.",
    )

    parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="Run the experiment with only a few batches for all "
        "datasets, to ensure code runs without crashing.",
    )

    parser.add_argument(
        "--debug_batches",
        type=int,
        default=2,
        help="Number of batches to run in debug mode.",
    )

    parser.add_argument(
        "--device",
        type=str,
        default="cuda:0",
        help="The device to run the experiment on (e.g. 'cuda:0')",
    )

    parser.add_argument(
        "--noprogressbar",
        default=False,
        action="store_true",
        help="This flag disables the data loop progressbars.",
    )

    parser.add_argument(
        "--ckpt_interval_minutes",
        type=float,
        help="Amount of time between saving intra-epoch checkpoints "
        "in minutes. If non-positive, intra-epoch checkpoints are not saved.",
        default=15,
    )

    parser.add_argument(
        "--log_file",
        type=Path,
        help="Amount of time between saving intra-epoch checkpoints "
        "in minutes. If non-positive, intra-epoch checkpoints are not saved.",
        default=None,
    )

    args = parser.parse_args().__dict__
    param_file = args.pop("param_file")

    return param_file, args
