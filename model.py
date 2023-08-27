# -*- coding: utf-8 -*-
"""model.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NsWfSm2L1lDstvnynDeu1LORkdM895vR
"""

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from pickle import dump, load
import numpy as np
import pandas as pd


DATASET_PATH = "https://raw.githubusercontent.com/evgpat/edu_stepik_from_idea_to_mvp/main/datasets/clients.csv"


def split_data(df: pd.DataFrame):
    df['satisfaction'] = df['satisfaction'].map({'neutral or dissatisfied' : 0, 'satisfied' : 1})
    data = df.loc[df['satisfaction'].isin([0, 1])]
    X = data.drop(['satisfaction', 'id'], axis=1)
    y = data['satisfaction']

    return X, y


def open_data():
    df = pd.read_csv(DATASET_PATH)

    return df


def preprocess_data(df: pd.DataFrame, test=True):
    df.dropna(inplace=True)

    if test:
        X_df, y_df = split_data(df)
    else:
        X_df = df

    categories = ['Inflight wifi service', 'Departure/Arrival time convenient', 'Ease of Online booking', 'Gate location', 'Food and drink', 'Online boarding', 'Seat comfort', 'Inflight entertainment', 'On-board service', 'Leg room service', 'Baggage handling', 'Checkin service', 'Inflight service', 'Cleanliness']
    for category in categories:
        X_df[category] = np.where(X_df[category] < 1, 1, X_df[category]) #согласно описанию, все оценки должны быть от 1 до 5, заменим нулевые на минимально возможные
        X_df[category] = np.where(X_df[category] > 5, 5, X_df[category]) #аналогично поступим с максимальными оценками
        category_mean = X_df[category].mean()
        X_df[category].fillna(category_mean, inplace=True) #пропуски заполним средним значением для каждой категории

    columns = ['Departure Delay in Minutes', 'Arrival Delay in Minutes']
    X_df = X_df.dropna(axis='index', how='any', subset=['Age'])
    X_df['Age'] = np.where(X_df['Age'] < 10, 10, X_df['Age'])
    for col in columns:
        X_df[col] = np.where(X_df[col] > 100, 100, X_df[col])
        col_mean = X_df[col].mean()
        X_df[col].fillna(col_mean, inplace=True)
    X_df['Flight Distance'] = np.where(X_df['Flight Distance'] > 7000, 7000, X_df['Flight Distance'])
    col_mean = X_df['Flight Distance'].mean()
    X_df['Flight Distance'].fillna(col_mean, inplace=True)

    X_df = X_df.dropna(axis='index', how='any', subset=['Gender', 'Customer Type', 'Type of Travel', 'Class'])

    X_df['Gender'] = X_df['Gender'].map({'Male' : 0, 'Female' : 1})
    X_df['Customer Type'] = X_df['Customer Type'].map({'disloyal Customer' : 0, 'Loyal Customer' : 1})
    X_df['Type of Travel'] = X_df['Type of Travel'].map({'Business travel' : 0, 'Personal Travel' : 1})


    if test:
        return X_df, y_df
    else:
        return X_df


def fit_and_save_model(X_df, y_df, path="data/model_weights.mw"):
    model = LogisticRegression()
    model.fit(X_df, y_df)

    test_prediction = model.predict(X_df)
    accuracy = accuracy_score(test_prediction, y_df)
    print(f"Model accuracy is {accuracy}")

    with open(path, "wb") as file:
        dump(model, file)

    print(f"Model was saved to {path}")


def load_model_and_predict(df, path="data/model_weights.mw"):
    with open(path, "rb") as file:
        model = load(file)

    prediction = model.predict(df)[0]
    # prediction = np.squeeze(prediction)

    prediction_proba = model.predict_proba(df)[0]
    # prediction_proba = np.squeeze(prediction_proba)

    encode_prediction_proba = {
        0: "Вам не понравится с вероятностью",
        1: "Вы будете удовлетворены с вероятностью"
    }

    encode_prediction = {
        0: "Сожалеем, вам лучше найти другую авиакомпанию",
        1: "Рады, что вам понравилось!"
    }

    prediction_data = {}
    for key, value in encode_prediction_proba.items():
        prediction_data.update({value: prediction_proba[key]})

    prediction_df = pd.DataFrame(prediction_data, index=[0])
    prediction = encode_prediction[prediction]

    return prediction, prediction_df


if __name__ == "__main__":
    df = open_data()
    X_df, y_df = preprocess_data(df)
    fit_and_save_model(X_df, y_df)
