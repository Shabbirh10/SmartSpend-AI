import joblib
import os
import pandas as pd
import sys
import warnings

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

    def _train_model(self):
        try:
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
            if repo_root not in sys.path:
                sys.path.insert(0, repo_root)
            from ml_engine.training.train_model import train
            train()
            return True
        except Exception as e:
            print(f"Error training model: {e}")
            return False

    def _load_model(self):
        try:
            if os.path.exists(self.model_path):
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    self.model = joblib.load(self.model_path)

                should_retrain = False
                for w in caught:
                    if w.category.__name__ == "InconsistentVersionWarning":
                        should_retrain = True
                        break

                if should_retrain:
                    print("Warning: Model pickle version mismatch detected. Retraining model for compatibility...")
                    self.model = None
                else:
                    print("ML Model loaded successfully.")
            else:
                print(f"Warning: ML model not found at {self.model_path}. Categorization will use fallback.")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

        if not self.model:
            if self._train_model() and os.path.exists(self.model_path):
                try:
                    self.model = joblib.load(self.model_path)
                    print("ML Model trained and loaded successfully.")
                except Exception as e:
                    print(f"Error loading newly trained model: {e}")

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
