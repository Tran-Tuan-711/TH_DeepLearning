import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download stopwords quietly
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords', quiet=True)

stop_words_en = set(stopwords.words('english'))
stemmer = PorterStemmer()


def clean_text(text):
    """
    Tiền xử lý text email tiếng Anh (SpamAssassin):
    - Lowercase
    - Xóa HTML tags, URLs, email addresses, số, ký tự đặc biệt
    - Loại bỏ stopwords tiếng Anh
    - Stemming (Porter Stemmer)
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r'<.*?>', ' ', text)           # HTML tags
    text = re.sub(r'http\S+|www\S+', ' ', text)  # URLs
    text = re.sub(r'\S+@\S+', ' ', text)         # Email addresses
    text = re.sub(r'\d+', ' ', text)              # Numbers
    text = re.sub(r'[^a-z\s]', ' ', text)        # Special characters

    words = text.split()
    words = [w for w in words if w not in stop_words_en]
    words = [stemmer.stem(w) for w in words]

    return " ".join(words)