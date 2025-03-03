import argparse
import os
import sys

from PyQt5.QtWidgets import QApplication

from playground import Recipe

os.environ['QT_QPA_PLATFORM'] = 'offscreen'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Large Multi-modal Model Playground')
    parser.add_argument('--exp-recipe',
                        type=str,
                        help='Path to the game config.',
                        default='configs/recipe/base.py')
    parser.add_argument('--agent-cfg',
                        type=str,
                        help='Path to the agent config.',
                        default='configs/agents/internvl/internvl2-1b.py')
    return parser.parse_args()


def main():
    app = QApplication(sys.argv)  # noqa

    args = parse_args()
    recipe = Recipe(args)
    recipe.run_experiments()


if __name__ == '__main__':
    main()
