import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import f1_score
import pandas as pd
import joblib

from backend.model import EmailDataset, SpamClassifier

# Load and preprocess data
data = pd.read_csv('emails.csv')  # expects 'text' and 'label' columns
print(data['label'].value_counts())
vectorizer = CountVectorizer(stop_words='english')
X = vectorizer.fit_transform(data['text']).toarray()
y = data['label'].values

# Save the vectorizer
joblib.dump(vectorizer, 'vectorizer.pkl')

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

train_dataset = EmailDataset(X_train, y_train)
test_dataset = EmailDataset(X_test, y_test)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32)

# Training setup
model = SpamClassifier(input_dim=X.shape[1])
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

best_f1 = 0

for epoch in range(10):
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

    print(f"Epoch {epoch + 1} - F1 Score: {f1:.4f}")
