import pickle
import time

import pandas as pd

def overunder_mapping(row):
    if row['Diff'] > 0:
        return 'OVER'
    elif row['Diff'] < 0:
        return 'UNDER'
    else:
        return 'PUSH'

def confidence_mapping(row):
    return int(abs(row['Diff']) / 2) + 1

timestr = time.strftime("%Y%m%d")
x = pd.read_csv('projections\\todays_player_data'+timestr+'.csv')

lines = pd.read_csv('lines.csv')
lines = lines[lines.Type == 'points']

model_path = 'SVC_Model.sav'
model = pickle.load(open(model_path, 'rb'))

scaler_path = 'scaler.pkl'
scaler = pickle.load(open(scaler_path, 'rb'))

cols = x.columns

x = scaler.transform(x)

x = pd.DataFrame(x, columns=[cols])

y_pred = model.predict(x)

lines['Prediction'] = y_pred.tolist()
lines['Diff'] = lines['Prediction'] - lines['Line']
lines['O/U'] = lines.apply(overunder_mapping, axis=1)
lines['Confidence Rating'] = lines.apply(confidence_mapping, axis=1)
lines = lines.sort_values(by=['Diff'], ascending=False, key=abs)

timestr = time.strftime("%Y%m%d")
lines.to_csv('predictions_'+timestr+'.csv')