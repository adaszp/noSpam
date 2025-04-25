from sacred import Experiment
from sacred.observers import FileStorageObserver
import itertools

from backend.constants import SACRED_OBSERVER_DIRECTORY
from backend.model import SpamClassifier
from utils import load_and_vectorize_data, prepare_dataloaders, train_model

# Initialize Sacred experiment
ex = Experiment('spam_classifier')
ex.observers.append(FileStorageObserver(SACRED_OBSERVER_DIRECTORY))


@ex.config
def config():
    epochs = 10
    batch_size = 32
    learning_rate = 0.001
    train_test_split_size = 0.2
    random_seed = 42


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
        learning_rate=learning_rate
    )

    ex.log_scalar('best_f1_score', best_f1)
    print(f"Best F1 Score: {best_f1:.4f}")


if __name__ == "__main__":
    # Define hyperparameters for the sweep
    epochs_list = [10, 25, 50]
    batch_sizes = [16, 32, 64]
    learning_rates = [0.01, 0.001, 0.0001]

    config_combinations = list(itertools.product(epochs_list, batch_sizes, learning_rates))

    for epoch, batch_size, lr in config_combinations:
        print(f"Running experiment with epochs={epoch}, batch_size={batch_size}, learning_rate={lr}")
        ex.run(config_updates={
            'epochs': epoch,
            'batch_size': batch_size,
            'learning_rate': lr,
            'train_test_split_size': 0.2,
            'random_seed': 42
        })
