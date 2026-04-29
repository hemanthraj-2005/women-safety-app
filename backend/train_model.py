import numpy as np
import pickle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

sentences = [
    "help me",
    "please help",
    "save me",
    "i am in danger",
    "emergency",
    "someone is following me",
    "i need help",
    "danger",
    "call police",
    "rescue me",
    "i am scared",
    "please save me",

    "hello how are you",
    "i am going home",
    "good morning",
    "where are you",
    "i am fine",
    "see you later",
    "let us go shopping",
    "i reached college",
    "call me later",
    "this is normal",
    "i am studying",
    "good night"
]

labels = [
    1,1,1,1,1,1,1,1,1,1,1,1,
    0,0,0,0,0,0,0,0,0,0,0,0
]

tokenizer = Tokenizer(num_words=1000, oov_token="<OOV>")
tokenizer.fit_on_texts(sentences)

sequences = tokenizer.texts_to_sequences(sentences)
padded = pad_sequences(sequences, maxlen=10, padding="post")

X_train, X_test, y_train, y_test = train_test_split(
    padded, np.array(labels), test_size=0.2, random_state=42
)

model = Sequential([
    Embedding(input_dim=1000, output_dim=16, input_length=10),
    GlobalAveragePooling1D(),
    Dense(16, activation="relu"),
    Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.fit(X_train, y_train, epochs=100, verbose=1)

loss, accuracy = model.evaluate(X_test, y_test)
print("Model Accuracy:", accuracy)

model.save("distress_model.h5")

with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

print("Model and tokenizer saved successfully.")