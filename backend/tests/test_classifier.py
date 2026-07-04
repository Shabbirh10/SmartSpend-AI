from app.services.classifier import classifier

def test_classifier_prediction():
    # Test that prediction returns a string category
    pred = classifier.predict("UBER *RIDE")
    assert isinstance(pred, str)
    assert len(pred) > 0

    pred_shop = classifier.predict("AMAZON MKTP")
    assert isinstance(pred_shop, str)
