import pandas as pd
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle

# Define allowed categories
allowed_categories = ['citizenship', 'pan']
# Get the absolute path of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Step 1: Load the data from the CSV file
# Updated the file path to point to the data folder
# Build the path to the CSV file inside the data folder
csv_path = os.path.join(script_dir, 'data', 'processed.csv')

# Load the data
df = pd.read_csv(csv_path)

# Ensure that 'text' and 'label' columns exist
if 'text' not in df.columns or 'label' not in df.columns:
    print("Error: CSV file does not contain 'text' and 'label' columns.")
    exit()

# Step 2: Prepare the data
X = df['text']  # Text data
y = df['label']  # Corresponding labels

# Step 3: Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Vectorize the text data (convert text to numerical features)
vectorizer = CountVectorizer(stop_words='english')
X_train_vect = vectorizer.fit_transform(X_train)
X_test_vect = vectorizer.transform(X_test)

# Step 5: Train the model (Naive Bayes classifier)
model = MultinomialNB()
model.fit(X_train_vect, y_train)

# Step 6: Make predictions on the test set and evaluate the model
y_pred = model.predict(X_test_vect)

# Print accuracy and classification report
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Step 7: Save the model and vectorizer for later use in the same folder (train_model)
with open('text_classifier_model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)
with open('vectorizer.pkl', 'wb') as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)

# Function to predict new text input with a confidence threshold
def predict_category(input_text, threshold=0.6):
    # Load the saved model and vectorizer
    with open('text_classifier_model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('vectorizer.pkl', 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
    
    # Vectorize the input text
    input_vect = vectorizer.transform([input_text])
    
    # Get the prediction probabilities and determine the maximum probability
    probs = model.predict_proba(input_vect)
    max_prob = probs.max()
    
    # Get the prediction result
    prediction = model.predict(input_vect)[0]
    
    # If the confidence is below threshold or prediction is not among allowed, mark as invalid
    if max_prob < threshold or prediction not in allowed_categories:
        return "Invalid document type"
    return prediction

# Step 8: User Input for Prediction
if __name__ == "__main__":
    while True:
        print("\nEnter the text to classify (or 'exit' to quit):")
        user_input = input()
        if user_input.lower() == 'exit':
            break
        
        # Get the prediction with confidence check
        result = predict_category(user_input)
        print(f"Predicted Category: {result}")
