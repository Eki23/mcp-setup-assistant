# Copyright (c) 2026 Christian Ekiza

"""Generic CLI for codebase-memory-mcp setup tools."""
import argparse
import sys
from typing import Callable


def run_cli(prog: str, description: str, init_fn: Callable, index_fn: Callable):
    """Build and run the CLI with init and index subcommands."""
    parser = argparse.ArgumentParser(prog=prog, description=description)
    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init", help="Set up MCP server config and agent rules for a project")
    init_parser.add_argument("--agent", action="append", choices=["amazonq", "cursor"], required=True, help="Target agent(s) to configure")

    # index
    index_parser = subparsers.add_parser("index", help="Index libraries and project-specific code")
    index_parser.add_argument("--venv", default=".venv", help="Path to the virtual environment (default: .venv)")
    index_parser.add_argument("--package", action="append", default=[], metavar="PACKAGE", help="Additional package to index (repeatable)")
    index_parser.add_argument("--folder", action="append", default=[], metavar="FOLDER", help="Additional folder to index (repeatable)")

    args = parser.parse_args()

    if args.command == "init":
        init_fn(args.agent)
    elif args.command == "index":
        index_fn(args.venv, args.package, args.folder)
    else:
        parser.print_help()
        sys.exit(1)
