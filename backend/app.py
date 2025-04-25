from fastapi import FastAPI
from pydantic import BaseModel
import torch
import joblib
from sentence_transformers import SentenceTransformer

from constants import MODEL_SAVE_PATH, VECTORIZER_PATH, EMBEDDING_MODEL_NAME
from model import SpamClassifier

app = FastAPI()

class EmailRequest(BaseModel):
    text: str

sentence_transformer = SentenceTransformer(EMBEDDING_MODEL_NAME)

model = SpamClassifier(input_dim=sentence_transformer.get_sentence_embedding_dimension())
model.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=torch.device('cpu')))
model.eval()

@app.post("/predict")
def predict_spam(email: EmailRequest):
    vec = sentence_transformer.encode([email.text])
    input_tensor = torch.tensor(vec, dtype=torch.float32)
    with torch.no_grad():
        output = model(input_tensor).item()
    prediction = 1 if output > 0.5 else 0
    return {"spam": bool(prediction), "confidence": float(output)}

@app.get("/hello")
def hello():
    return {"message": "Api works"}