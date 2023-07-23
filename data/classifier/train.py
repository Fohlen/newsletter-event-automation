import json
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
import numpy as np

from src.message import Message

if __name__ == "__main__":
    with open("messages.jsonl") as messages_fp, \
            open("labels.txt") as labels_fp, \
            open("pipeline.pkl", "wb") as pipeline_fp:
        messages: list[Message] = [json.loads(line) for line in messages_fp]
        labels = np.array([int(line) for line in labels_fp])

        X_train, X_test, y_train, y_test = train_test_split(
            [message["content"] for message in messages], labels, test_size=0.33, random_state=42
        )

        pipeline = Pipeline(
            [
                ("vect", TfidfVectorizer()),
                ("clf", LinearRegression()),
            ]
        )

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        print(classification_report(
            np.rint(y_pred).astype(int).reshape((-1)),
            y_test,
            target_names=["non_event", "event"]
        ))

        pickle.dump(pipeline, pipeline_fp)

