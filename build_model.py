from  sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, SVR
import pandas as pd
from sklearn.metrics import r2_score
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout
import pickle

# read scraped player data
data_file = 'player_data.csv'
df = pd.read_csv(data_file, header=0)

# drop whitespace, nulls, and initial index column
df.columns = df.columns.str.strip()
df = df.dropna()
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# dropping points from x dataset, adding to y
x = df.drop(['PTS'], axis=1)
y = df['PTS']

# splitting data into train test data
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.01)

# get column names
cols = x_train.columns
scaler = StandardScaler()

# transform data
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)

x_train = pd.DataFrame(x_train, columns=[cols])
x_test = pd.DataFrame(x_test, columns=[cols])
'''
model = Sequential()
model.add(Dense(128, input_dim=x_train.shape[1], activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(1))  # Output layer with one neuron for predicting points
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(x_train, y_train, epochs=20, batch_size=32, validation_data=(x_test, y_test), verbose=True)

mlp_pred = model.predict(x_test)

mae = mean_absolute_error(y_test, mlp_pred)
r2 = r2_score(y_test, mlp_pred)

print('MLP')
print('Mean Absolute Error: ', mae)
print('R2: ', r2)
'''

# build model, fit, and predict
# svc = SVC()
svc = SVR()
svc.fit(x_train, y_train)
svm_y_pred = svc.predict(x_test)

# performance metrics
mae = mean_absolute_error(y_test, svm_y_pred)
r2 = r2_score(y_test, svm_y_pred)

print('SVM')
print('Mean Absolute Error: ', mae)
print('R2: ', r2)

filename = 'SVC_Model.sav'
pickle.dump(svc, open(filename, 'wb'))
pickle.dump(scaler, open('scaler.pkl', 'wb'))

