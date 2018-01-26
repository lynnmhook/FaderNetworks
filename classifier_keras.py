
import preprocess
from src.loader import load_images
from collections import namedtuple 

def nt(dictionary):
    return namedtuple('GenericDict', dictionary.keys())(**dictionary)


images, attributes = load_images(nt({'debug':False, 'attr': [('Male',2)], 'n_attr':2}))



import keras
from keras.layers import Dense, Flatten, Conv2D, MaxPooling2D
from keras.models import Sequential
from keras.optimizers import Adam


x_train = images[0].numpy().transpose((0,2,3,1)) / 255.0
x_test = images[1].numpy().transpose((0,2,3,1)) / 255.0

y_train = attributes[0].numpy()
y_test = attributes[1].numpy()

model = Sequential()
model.add(Conv2D(64, (5,5), activation='relu', input_shape=x_train.shape[1:]))
model.add(MaxPooling2D((2,2)))
model.add(Conv2D(64, (3,3), activation='relu', ))
model.add(MaxPooling2D((2,2)))
model.add(Flatten())
model.add(Dense(2, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer=Adam(),
              metrics=['accuracy'])

model.summary()


batch_size = 32
epochs = 20
model.fit(x_train, y_train, validation_data=[x_test, y_test], batch_size = batch_size, epochs=epochs)

