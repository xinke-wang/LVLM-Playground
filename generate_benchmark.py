import argparse
import os

from playground.benchmark import Generator

os.environ['QT_QPA_PLATFORM'] = 'offscreen'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate offline benchmark for LVLM-Playground')
    parser.add_argument('--benchmark-setting',
                        type=str,
                        help='Path to the benchmark setting config.',
                        default='configs/base.py')
    return parser.parse_args()


def main():
    args = parse_args()
    generator = Generator(args.benchmark_setting)
    generator.generate_benchmark()


if __name__ == '__main__':
    main()
