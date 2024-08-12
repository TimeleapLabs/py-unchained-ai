#!/usr/bin/env python

import argparse

from .servers.ws import main as ws_main
from .servers.us import main as us_main


def main():
    parser = argparse.ArgumentParser(
        prog='unchained-ai',
        description='Unchained AI Plugin Command-Line Interface')

    # Create subparsers for 'ws' and 'us' commands
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # Create the parser for the 'ws' command
    parser_ws = subparsers.add_parser('ws', help='WebSocket server')
    parser_ws.add_argument('--port', type=int, required=True,
                           help='Port number for the WebSocket server')

    # Create the parser for the 'us' command
    parser_us = subparsers.add_parser('us', help='Unix socket')
    parser_us.add_argument('--file', type=str, required=True,
                           help='Path to the Unix socket file')

    # Parse the arguments
    args = parser.parse_args()

    # Call the appropriate function based on the command
    if args.command == 'ws':
        ws_main(args.port)
    elif args.command == 'us':
        us_main(args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
