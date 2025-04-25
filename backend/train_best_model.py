import json
from sacred import Experiment

from backend.constants import MODEL_SAVE_PATH
from backend.model import SpamClassifier
from utils import load_and_vectorize_data, prepare_dataloaders, train_model

ex = Experiment('spam_classifier')

# Wczytanie najlepszej konfiguracji
with open('best_config.json', 'r') as f:
    best_configuration = json.load(f)

@ex.config
def config():
    epochs = best_configuration['epochs']
    batch_size = best_configuration['batch_size']
    learning_rate = best_configuration['learning_rate']
    train_test_split_size = best_configuration['train_test_split_size']
    random_seed = best_configuration['random_seed']

@ex.automain
def main(epochs, batch_size, learning_rate, train_test_split_size, random_seed):
    X, y = load_and_vectorize_data()
    train_loader, test_loader, input_dim = prepare_dataloaders(
        X, y, batch_size=batch_size, test_size=train_test_split_size, random_seed=random_seed
    )

    model = SpamClassifier(input_dim=input_dim)

    best_f1 = train_model(
        model=model,
        train_loader=train_loader,
        test_loader=test_loader,
        epochs=epochs,
        learning_rate=learning_rate,
        model_save_path=MODEL_SAVE_PATH
    )

    print(f"Best F1 Score: {best_f1:.4f}")
