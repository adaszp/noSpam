from fastapi import FastAPI
from pydantic import BaseModel
import torch
import joblib

from model import SpamClassifier

app = FastAPI()

class EmailRequest(BaseModel):
    text: str

vectorizer = joblib.load("vectorizer.pkl")
model = SpamClassifier(input_dim=len(vectorizer.get_feature_names_out()))
model.load_state_dict(torch.load("best_model.pth", map_location=torch.device('cpu')))
model.eval()

@app.post("/predict")
def predict_spam(email: EmailRequest):
    vec = vectorizer.transform([email.text]).toarray()
    input_tensor = torch.tensor(vec, dtype=torch.float32)
    with torch.no_grad():
        output = model(input_tensor).item()
    prediction = 1 if output > 0.5 else 0
    return {"spam": bool(prediction), "confidence": float(output)}

@app.get("/hello")
def hello():
    return {"message": "Api works"}