import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader
import torch
import torch.nn as nn
import torch.optim as optim

from backend.constants import VECTORIZER_PATH, EMBEDDING_MODEL_NAME
from backend.model import EmailDataset, SpamClassifier
from sentence_transformers import SentenceTransformer


def load_and_vectorize_data(csv_path='./emails.csv', vectorizer_path=VECTORIZER_PATH):
    sentence_transformer = SentenceTransformer(EMBEDDING_MODEL_NAME, cache_folder='./transformer_cache')
    data = pd.read_csv(csv_path)

    X = sentence_transformer.encode(data['text'].tolist(), show_progress_bar=True)
    y = data['label'].values
    return X, y


def prepare_dataloaders(X, y, batch_size, test_size, random_seed):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_seed)

    train_dataset = EmailDataset(X_train, y_train)
    test_dataset = EmailDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    return train_loader, test_loader, X.shape[1]


def train_model(model, train_loader, test_loader, epochs, learning_rate, model_save_path=None):
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    best_f1 = 0

    for epoch in range(epochs):
        model.train()
        for inputs, labels in train_loader:
            outputs = model(inputs).squeeze()
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        model.eval()
        all_preds = []
        all_labels = []
        with torch.no_grad():
            for inputs, labels in test_loader:
                outputs = model(inputs).squeeze()
                preds = (outputs > 0.5).float()
                all_preds.extend(preds.tolist())
                all_labels.extend(labels.tolist())

        f1 = f1_score(all_labels, all_preds)
        if f1 > best_f1:
            best_f1 = f1
            if model_save_path:
                torch.save(model.state_dict(), model_save_path)
                print(f'Model saved to: {model_save_path}')

        print(f"Epoch {epoch + 1} - F1 Score: {f1:.4f}")

    return best_f1
