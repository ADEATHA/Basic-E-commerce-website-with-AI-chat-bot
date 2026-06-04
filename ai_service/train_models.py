import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, LSTM, Bidirectional, Dense, Embedding
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Set random seed for reproducibility
tf.random.set_seed(42)
np.random.seed(42)

def train_and_compare_models():
    # 1. Load Data
    data_path = 'ai_service/data/data_user500.csv'
    if not os.path.exists(data_path):
        # Fallback for relative path
        data_path = 'data/data_user500.csv'
        
    df = pd.read_csv(data_path)
    
    # 2. Preprocessing
    # We will predict the next CATEGORY based on the previous categories of the user
    le = LabelEncoder()
    df['category_id'] = le.fit_transform(df['category'])
    num_classes = len(le.classes_)
    
    # Create sequences for each user
    sequences = []
    targets = []
    window_size = 3
    
    for user_id, group in df.groupby('user_id'):
        cat_ids = group['category_id'].tolist()
        if len(cat_ids) > window_size:
            for i in range(len(cat_ids) - window_size):
                sequences.append(cat_ids[i:i + window_size])
                targets.append(cat_ids[i + window_size])
                
    X = np.array(sequences)
    y = np.array(targets)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. Model Building Function
    def build_model(model_type='RNN'):
        model = Sequential()
        model.add(Embedding(input_dim=num_classes, output_dim=16, input_length=window_size))
        
        if model_type == 'RNN':
            model.add(SimpleRNN(32))
        elif model_type == 'LSTM':
            model.add(LSTM(32))
        elif model_type == 'biLSTM':
            model.add(Bidirectional(LSTM(32)))
            
        model.add(Dense(num_classes, activation='softmax'))
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        return model

    # 4. Training
    results = {}
    models = ['RNN', 'LSTM', 'biLSTM']
    
    os.makedirs('ai_service/plots', exist_ok=True)
    os.makedirs('ai_service/models', exist_ok=True)
    
    plt.figure(figsize=(12, 5))
    
    for m_type in models:
        print(f"\nTraining {m_type}...")
        model = build_model(m_type)
        history = model.fit(X_train, y_train, epochs=15, batch_size=32, validation_data=(X_test, y_test), verbose=0)
        
        acc = history.history['accuracy'][-1]
        val_acc = history.history['val_accuracy'][-1]
        results[m_type] = {'history': history, 'val_acc': val_acc, 'model': model}
        print(f"{m_type} - Val Accuracy: {val_acc:.4f}")
        
        plt.plot(history.history['val_accuracy'], label=f'{m_type} Val Acc')

    # Evaluation & Best Model Selection
    plt.title('Validation Accuracy Comparison')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig('ai_service/plots/accuracy_comparison.png')
    
    # Find best model
    best_type = max(results, key=lambda k: results[k]['val_acc'])
    print(f"\nBest Model: {best_type}")
    
    best_model = results[best_type]['model']
    # Save as .keras inside the container-friendly path
    best_model.save('models/model_best.keras')
    
    # Save Label Encoder for later use in app.py
    import joblib
    joblib.dump(le, 'models/category_le.pkl')
    
    print("Training complete. Best model saved.")

if __name__ == "__main__":
    train_and_compare_models()
