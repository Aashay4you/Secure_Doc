import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import joblib
import os

data = {
    'text': [
        "public holiday notice for all staff",
        "canteen menu for next week lunch",
        "general office guidelines and dress code",
        "meeting regarding annual sports day",
        "project timeline and deadlines for internal use",
        "internal memo regarding software updates",
        "employee handbook and policy",
        "confidential password for the server is admin123",
        "salary slip for the month of august",
        "medical report and diagnosis of patient",
        "top secret military strategy and nuclear codes",
        "credit card details and banking pin",
        "social security number and private address"
    ],
    'label': [
        'Low', 'Low', 'Low', 'Low',           # Public
        'Medium', 'Medium', 'Medium',         # Internal
        'High', 'High', 'High', 'High', 'High', 'High' # Sensitive
    ]
}

df = pd.DataFrame(data)

# 2. Vectorization (Text -> Numbers)
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(df['text'])
y = df['label']

# 3. Model Training (SVM)
# Probability=True allows us to see confidence scores if needed
classifier = SVC(kernel='linear', probability=True)
classifier.fit(X, y)

# 4. Save the Model
if not os.path.exists('models'):
    os.makedirs('models')

joblib.dump(vectorizer, 'models/vectorizer.pkl')
joblib.dump(classifier, 'models/classifier.pkl')

print("✅ Model Trained and Saved to 'models/' folder successfully!")