import re
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics.pairwise import linear_kernel


class QuestionAnsweringModel:
    def __init__(self, df):
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('stopwords')
        
        model, tfidf_vectorizer, vectorized_questions, df = self.train_model(df)
        
        self.model = model
        self.tfidf_vectorizer = tfidf_vectorizer
        self.vectorized_questions = vectorized_questions
        self.df = df
  
    def preprocess_text(self, text):
        text = text.lower()

        text = re.sub(r'[^\w\s]', '', text)

        words = nltk.word_tokenize(text)

        lemmatizer = WordNetLemmatizer()

        words = [lemmatizer.lemmatize(word) for word in words]

        stop_words = set(stopwords.words('english'))

        words = [word for word in words if word not in stop_words]

        text = ' '.join(words).strip()

        return text

    def train_model(self, df):

        df['preprocessed_questions'] = df['question'].apply(self.preprocess_text)

        # TF-IDF Vectorization
        tfidf_vectorizer = TfidfVectorizer()
        vector_questions = tfidf_vectorizer.fit_transform(df['preprocessed_questions'])

        # Split into training and testing datasets
        X_train, X_test, y_train, y_test = train_test_split(vector_questions, df['tag'], test_size=0.2, random_state=42)

        # Training a Random Forest Classifier
        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        # Make predictions on the testing set
        y_pred = model.predict(X_test)

        # Calculate accuracy and print the classification report
        accuracy = accuracy_score(y_test, y_pred)
        print("Accuracy:", accuracy)
        print(classification_report(y_test, y_pred))

        return model, tfidf_vectorizer, vector_questions, df

    def generate_response(self, question):

        tfidf_vectorizer = self.tfidf_vectorizer
        tfidf_matrix = self.vectorized_questions
        data = self.df
        
        preprocessed_question = self.preprocess_text(question)
        vectorized_question = tfidf_vectorizer.transform([preprocessed_question])
        
        tag = self.model.predict(vectorized_question)[0]
        
        df_filtered = data[data['tag'] == tag]
        
        X_filtered = tfidf_vectorizer.transform(df_filtered['preprocessed_questions'])
        
        print("question:", question)
        print("predicted tag:", tag)
        print("predicted tag questions:", df_filtered['preprocessed_questions'])
        print("predicted tag answers:", df_filtered['answer'])

        question_vector = tfidf_vectorizer.transform([preprocessed_question])

        # Calculate cosine similarities between the input question and all questions in the dataset
        cosine_similarities = linear_kernel(question_vector, X_filtered).flatten()
        print("cosine_similarities:", cosine_similarities)
        
        # Find the index of the most similar question
        np.random.seed(41)
        most_similar_index = np.argmax(cosine_similarities)
        print("most_similar_index:", most_similar_index)

        # Return the answer of the most similar question
        return df_filtered.iloc[most_similar_index]['answer']

import pandas as pd
df = pd.read_csv("data/final.csv", sep=";")
model = QuestionAnsweringModel(df)


question = "Can I train ML models with data prepared in Data Wrangler?"
response = model.generate_response(question)
print("Question:", question)
print("Answer:", response)


