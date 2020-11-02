import numpy as np
import pykitml as pk

# Load dataset
train_inputs, train_outputs, test_inputs, test_outputs, dev_inputs, dev_outputs = pk.load('Data/traindata.pkl')
train_inputs, test_inputs, dev_inputs = train_inputs/255, test_inputs/255, dev_inputs/255

# Compress inputs using PCA, pick 1000 random examples for PCA
rand_indices = np.random.choice(train_inputs.shape[0], 1000, replace=False)
pca = pk.PCA(train_inputs[rand_indices], no_components=64)
print('PCA Retention:', pca.retention)

# Transform dataset
train_inputs = pca.transform(train_inputs)
test_inputs = pca.transform(test_inputs)
dev_inputs = pca.transform(dev_inputs)

# Save pca model
pk.save(pca, 'pca.pkl')

# Start hyperparameter search
search = pk.RandomSearch()
for alpha, decay, decay_freq, in search.search(10, 2, 5, 
    [-4, -3, 'log'], [0.9, 1, 'float'], [50, 100, 'int']):
    
    model = pk.LSTM([64, 100, 3])
    
    model.train(
        training_data=train_inputs,
        targets=train_outputs, 
        batch_size=200, 
        epochs=10000, 
        optimizer=pk.Adam(learning_rate=alpha, decay_rate=decay), 
        testing_data=test_inputs,
        testing_targets=test_outputs,
        testing_freq=1000,
        decay_freq=decay_freq
    )
    
    cost = model.cost(test_inputs, test_outputs)
    search.set_cost(cost)
    
    # Save the best model
    if(search.best): pk.save(model, 'best.pkl')

# Load the best model
model = pk.load('best.pkl')

# Show performance
accuracy = model.accuracy(train_inputs, train_outputs)
print('Train Accuracy:', accuracy)        
accuracy = model.accuracy(test_inputs, test_outputs)
print('Test Accuracy:', accuracy)        
accuracy = model.accuracy(dev_inputs, dev_outputs)
print('Dev Accuracy:', accuracy)        

# Plot performance
model.plot_performance()

# Show confusion matrix
model.confusion_matrix(dev_inputs, dev_outputs)
model.confusion_matrix(train_inputs, train_outputs)
