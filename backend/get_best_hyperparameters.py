import json
import os

from backend.constants import SACRED_OBSERVER_DIRECTORY

directory = SACRED_OBSERVER_DIRECTORY
best_config = {}
best_metric = 0
for experiment_dir_name in os.listdir(directory):
    if experiment_dir_name[0] != '_':
        experiment_dir = os.path.join(directory, experiment_dir_name)
        with open(os.path.join(experiment_dir, 'metrics.json')) as json_file:
            metrics = json.load(json_file)

        f1_score = metrics['best_f1_score']['values'][0]
        if f1_score > best_metric:
            best_metric = f1_score
            with open(os.path.join(experiment_dir, 'config.json')) as json_file:
                best_config = json.load(json_file)

print('best config ', best_config)
print('best metric ', best_metric)

with open('best_config.json', 'w') as f:
    json.dump(best_config, f)
