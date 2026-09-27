import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import emlearn

import data_to_stats as dts

DATASET_FILENAME = 'gesture_dataset.csv'
PROCESSED_TRAIN_FILENAME = 'stats_train_dataset.csv'
PROCESSED_TEST_FILENAME = 'stats_test_dataset.csv'

# load raw data
raw_df = pd.read_csv(DATASET_FILENAME)

# split rows into training and testing groups
train_raw, test_raw = train_test_split(raw_df, test_size=0.2, random_state=42, stratify=raw_df['gesture_id'])

# process into stats
train_df = dts.process_df_to_stats(train_raw)
test_df = dts.process_df_to_stats(test_raw)

# saves stats
train_df.to_csv(PROCESSED_TRAIN_FILENAME, index=False, float_format='%.6f')
test_df.to_csv(PROCESSED_TEST_FILENAME, index=False, float_format='%.6f')

X_train = train_df.drop('gesture_id', axis=1)
y_train = train_df['gesture_id']

X_test = test_df.drop('gesture_id', axis=1)
y_test = test_df['gesture_id']

# model init
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# predict on unseen ones
y_pred = clf.predict(X_test)

# eval
acc = accuracy_score(y_test, y_pred)
print(f"True Out-of-Sample Accuracy Score: {acc * 100:.2f}%\n")

print("Classification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\n" + "=" * 40)

# save to ESP32 folder
FILENAME = 'sketch/model.h'
cmodel = emlearn.convert(clf, dtype='float', method='inline')
cmodel.save(file=FILENAME, name='RandomForest')

print(f"\nSaved the model to {FILENAME}")