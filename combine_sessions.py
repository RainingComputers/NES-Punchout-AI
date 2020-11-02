import random

import numpy as np
import pykitml as pk

def combine(files):
    # Combine files into numpy arrays
    inputs, outputs = pk.load(files[0])

    for file in files[1:]:
        file_inputs, file_outputs = pk.load(file)

        inputs = np.append(inputs, (file_inputs), axis=0)
        outputs = np.append(outputs, (file_outputs), axis=0)

    return inputs, outputs

train_files = [f'Data/session{x}.pkl' for x in range(1, 51)] \
    + [f'Data/knockout_session{x}.pkl' for x in range(1, 21)] 

test_files = [f'Data/session{x}.pkl' for x in range(51, 61)] \
    + [f'Data/knockout_session{x}.pkl' for x in range(21, 26)] 

dev_files = [f'Data/session{x}.pkl' for x in range(61, 71)] \
    + [f'Data/knockout_session{x}.pkl' for x in range(26, 31)] 

# Shuffle files
random.shuffle(train_files)
random.shuffle(test_files)
random.shuffle(dev_files)

# Combine files into numpy arrays
train_inputs, train_outputs = combine(train_files)
test_inputs, test_outputs = combine(test_files)
dev_inputs, dev_outputs = combine(dev_files)

# Save them
pk.save((train_inputs, train_outputs, test_inputs, test_outputs, dev_inputs, dev_outputs), 'Data/traindata.pkl')