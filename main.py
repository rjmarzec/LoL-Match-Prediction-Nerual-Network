# Code Taken from: https://www.tensorflow.org/tutorials/keras/basic_text_classification

from __future__ import absolute_import, division, print_function

import tensorflow as tf
from tensorflow import keras
from keras.callbacks import TensorBoard
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np

print('TF Version: ' + tf.__version__)

#############################################
# Download the Riot Dataset #################
#############################################


print('\tDownloading Test Dataset...')
def get_sheet():
    # GSpread Setup
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('[REDACTED]',scope)
    gc = gspread.authorize(credentials)
    return gc.open_by_key('[REDACTED]').sheet1
sheet = get_sheet()
match_ids = sheet.range(3, 1, 2003, 1)
input_label_list_from_sheet = sheet.range(3, 2, 2003, 2)
input_data_list_from_sheet = sheet.range(3, 17, 2003, 17)
input_label_list = []
input_data_list = []
for i in range(2000):
    if int(match_ids[i].value) != 0:
        input_label_list.append('0' if input_label_list_from_sheet[i].value == 'Red' else '1')

        input_data_list.append(input_data_list_from_sheet[i].value.split(','))
input_labels_doc = open('input_labels.txt', 'w')
input_labels_doc.write(str(input_label_list))
input_labels_doc.close()
input_data_doc = open('input_data.txt', 'w')
input_data_doc.write(str(input_data_list))
input_data_doc.close()


#############################################
# Prepare the Data ##########################
#############################################
print('\tPrepare the Data...')

largest_value = 0
for dataset_index in range(len(input_data_list)):
    for datapoint_index in range(len(input_data_list[dataset_index])):
        input_data_list[dataset_index][datapoint_index] = int(input_data_list[dataset_index][datapoint_index])
        input_label_list[dataset_index] = int(input_label_list[dataset_index])
        if input_data_list[dataset_index][datapoint_index] > 1550741400000:
            input_data_list[dataset_index][datapoint_index] = (input_data_list[dataset_index][datapoint_index] - 1550741400000)/3600000
        if input_data_list[dataset_index][datapoint_index] > largest_value:
            largest_value = input_data_list[dataset_index][datapoint_index]

input_data_np_array = np.array(input_data_list)
input_label_np_array = np.array(input_label_list)

train_data = keras.preprocessing.sequence.pad_sequences(input_data_list[0:1400], maxlen=361, value=0, padding='post')
test_data = keras.preprocessing.sequence.pad_sequences(input_data_list[1400:1800], maxlen=361, value=0, padding='post')
val_data = keras.preprocessing.sequence.pad_sequences(input_data_list[1800:], maxlen=361, value=0, padding='post')


#############################################
# Build The Model ###########################
#############################################
print('\tPrepare the Data...')
# input shape is the vocabulary count used for the movie reviews (10,000 words)
model = keras.Sequential()
model.add(keras.layers.Embedding(largest_value + 1, 8))
model.add(keras.layers.GlobalAveragePooling1D())
model.add(keras.layers.Dropout(0.5))
model.add(keras.layers.Dense(8, activation=tf.nn.relu))
model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))
model.summary()
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])

tbCallback = keras.callbacks.TensorBoard(log_dir='./logs', histogram_freq=0, write_graph=True, write_grads=False,
                                         write_images=False, embeddings_freq=0, embeddings_layer_names=None,
                                         embeddings_metadata=None, embeddings_data=None, update_freq='epoch')


#############################################
# Create a Validation Set ###################
#############################################
print('\tCreate a Validation Set...')
train_labels = input_label_np_array

x_val = val_data
partial_x_train = train_data[0:1400]
y_val = train_labels[1800:]
partial_y_train = train_labels[0:1400]


#############################################
# Train the Model ###########################
#############################################
print('\tTrain the Model...')
history = model.fit(partial_x_train, partial_y_train, epochs=20, validation_data=(x_val, y_val),
                    verbose=2, shuffle=True, callbacks=[tbCallback])


#############################################
# Evaluate the Model ########################
#############################################
print('\tEvaluate the Model...')
results = model.evaluate(test_data, input_label_np_array[1400:1800])
print(results)

red_win_counter = 0.0
for result in input_label_list:
    if result == 1:
        red_win_counter += 1
print("\nRed Win Percentage: ")
print((red_win_counter/len(input_label_list)))
print("Blue Win Percentage: ")
print(((len(input_label_list) - red_win_counter)/len(input_label_list)))
