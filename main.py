#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Entry point for the OriginalAkinator game.
Run this file to start the game.
"""

import os
import sys
import argparse


def main():
    """Main function to run the Akinator game."""
    # Add the src directory to the path
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    if src_dir not in sys.path:
        sys.path.append(src_dir)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the OriginalAkinator game")
    parser.add_argument("--cli", action="store_true", help="Run in command line interface mode")
    args = parser.parse_args()

    if args.cli:
        # Run in CLI mode
        from src.akinator import play_game
        play_game()
    else:
        # Run in GUI mode
        try:
            import tkinter
            from src.akinator_gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"Error importing tkinter: {e}")
            print("Falling back to CLI mode...")
            from src.akinator import play_game
            play_game()


if __name__ == "__main__":
    main()
