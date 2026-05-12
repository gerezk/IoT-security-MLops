from sklearn import metrics
from typing import Tuple


def evaluate_model(model, x_test, y_test) -> Tuple[float, float]:
    """
    Evaluate the model on the given test data.
    :param model: sklearn trained model
    :param x_test:
    :param y_test:
    :return: accuracy, weighted f1-score
    """

    y_pred = model.predict(x_test)

    acc = metrics.accuracy_score(y_test, y_pred)
    f1 = metrics.f1_score(y_test, y_pred, average='weighted')

    return acc, f1