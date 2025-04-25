import json

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import f1_score
import pandas as pd
import joblib
from sacred import Experiment

from backend.model import EmailDataset, SpamClassifier

# Initialize Sacred experiment
ex = Experiment('spam_classifier')

with open('best_config.json', 'r') as f:
    best_configuration = json.load(f)


@ex.config
def config():
    epochs = best_configuration['epochs']
    batch_size = best_configuration['batch_size']
    learning_rate = best_configuration['learning_rate']
    train_test_split_size = best_configuration['train_test_split_size']
    random_seed = best_configuration['random_seed']


# Load and preprocess data
@ex.automain
def main(epochs, batch_size, learning_rate, train_test_split_size, random_seed):
    data = pd.read_csv('emails.csv')  # expects 'text' and 'label' columns
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(data['text']).toarray()
    y = data['label'].values

    # Save the vectorizer
    joblib.dump(vectorizer, 'vectorizer.pkl')

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=train_test_split_size, random_state=random_seed)

    train_dataset = EmailDataset(X_train, y_train)
    test_dataset = EmailDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    # Model, criterion, and optimizer setup
    model = SpamClassifier(input_dim=X.shape[1])
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    best_f1 = 0

    # Training loop
    for epoch in range(epochs):
        model.train()
        for inputs, labels in train_loader:
            outputs = model(inputs).squeeze()
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # Evaluation
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
            torch.save(model.state_dict(), 'best_model.pth')
