import glob
import json
import os
from math import pi

import matplotlib.pyplot as plt


def load_evaluation_results(results_dir='evaluation_results'):
    """Load all evaluation result JSON files from the specified directory."""
    print(f'Scanning directory: {results_dir}')
    result_files = glob.glob(os.path.join(results_dir, '*_results.json'))
    print(f'Found files: {result_files}')

    models_data = {}

    if not result_files:
        print(f"No evaluation result files found in '{results_dir}'.")
        return None, {}

    print(f'Loading first file to determine categories: {result_files[0]}')
    with open(result_files[0], 'r') as f:
        first_data = json.load(f)
        weighted_summary = first_data.get('weighted_summary', {})
        categories = list(weighted_summary.keys())

    for file_path in result_files:
        model_name = os.path.splitext(os.path.basename(file_path))[0].replace(
            '_results', '')
        print(f'Processing file: {file_path} (Model: {model_name})')
        with open(file_path, 'r') as f:
            data = json.load(f)
            weighted_summary = data.get('weighted_summary', {})
            models_data[model_name] = {
                task: weighted_summary.get(task,
                                           {}).get('weighted_average', 0)
                for task in categories
            }
    return categories, models_data


def create_radar_chart(categories, models_data, output_file='radar_chart.pdf'):
    """Create a single radar chart with task-specific normalization."""
    if not categories or not models_data:
        print('No data to plot.')
        return

    print(f'Categories for radar chart: {categories}')
    print(f'Models data for plotting: {json.dumps(models_data, indent=4)}')

    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(12, 9), subplot_kw=dict(polar=True))
    task_ranges = {}
    for task in categories:
        task_values = [scores[task] for scores in models_data.values()]
        min_val = min(task_values)
        max_val = max(task_values) if max(task_values) > min(
            task_values) else min(task_values) + 1
        task_ranges[task] = (min_val, max_val)
        print(f'Task: {task}, Min: {min_val}, Max: {max_val}')

    for model, scores in models_data.items():
        values = [(scores[task] - task_ranges[task][0]) /
                  (task_ranges[task][1] - task_ranges[task][0])
                  if task_ranges[task][1] > task_ranges[task][0] else 0
                  for task in categories]
        values += values[:1]
        print(f'Normalized values for {model}: {values[:-1]}')

        ax.plot(angles, values, linewidth=1, linestyle='solid', label=model)
        ax.fill(angles, values, alpha=0.1)

    plt.xticks(angles[:-1], categories, fontsize=18, rotation=90)
    ax.set_yticklabels([f'{tick:.2f}' for tick in ax.get_yticks()],
                       fontsize=10)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
    plt.savefig(output_file, format='pdf', bbox_inches='tight')
    print(f"Radar chart saved to '{output_file}'")
    plt.close()


def main():
    results_dir = 'evaluation_results'
    categories, models_data = load_evaluation_results(results_dir)
    if models_data:
        create_radar_chart(categories, models_data)
    else:
        print('Failed to load data; radar chart not generated.')


if __name__ == '__main__':
    main()
