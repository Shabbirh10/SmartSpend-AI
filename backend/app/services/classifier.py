import joblib
import os
import pandas as pd

class TransactionClassifier:
    def __init__(self):
        # Adjust path to where the model will be saved relative to this file
        # Assuming app/services/classifier.py -> ../../../ml_engine/models/classifier.pkl
        # Or ideally, copy the model to backend/app/models/ during deployment
        self.model_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../../../ml_engine/models/classifier.pkl'
        ))
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print("ML Model loaded successfully.")
            else:
                print(f"Warning: ML model not found at {self.model_path}. Categorization will use fallback.")
        except Exception as e:
            print(f"Error loading model: {e}")

    def predict(self, description):
        if not self.model:
            return "Uncategorized"
        try:
            # Predict expects a list/series
            prediction = self.model.predict([description])
            return prediction[0]
        except Exception as e:
            print(f"Prediction error: {e}")
            return "Uncategorized"

classifier = TransactionClassifier()
