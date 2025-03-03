import argparse
import json
import os

from playground.evaluator import Metric


def parse_args():
    parser = argparse.ArgumentParser(description='LVLM-Playground Evaluation')
    parser.add_argument('record_path',
                        type=str,
                        help='Path to the experiment results JSON file.')
    parser.add_argument('--annotation_dir',
                        type=str,
                        default='./benchmark',
                        help='Directory containing annotation JSON files')
    parser.add_argument('--output_path',
                        type=str,
                        default=None,
                        help='Path to save the evaluation results JSON file')
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.exists(args.record_path):
        print(f"Error: Record file '{args.record_path}' does not exist.")
        return
    if not os.path.exists(args.annotation_dir):
        print(f"Error: Annotation '{args.annotation_dir}' does not exist.")
        return

    if args.output_path is None:
        record_filename = os.path.splitext(os.path.basename(
            args.record_path))[0]
        output_path = os.path.join('./evaluation_results',
                                   f'{record_filename}_results.json')
    else:
        output_path = args.output_path

    print('Starting evaluation...')
    metric = Metric(args.record_path, args.annotation_dir)
    scores = metric.evaluate_all()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    metric.save_evaluation(output_path)
    print(f"Evaluation results saved to '{output_path}'")

    print('\nDetailed Evaluation Results:')
    print(json.dumps(scores, indent=4))

    print('\nGame Difficulty Weighted Summary:')
    for task in metric.weighted_summary:
        weighted_avg = metric.weighted_summary[task]['weighted_average']
        print(f'{task}: Weighted Average Score = {weighted_avg:.4f}')


if __name__ == '__main__':
    main()
