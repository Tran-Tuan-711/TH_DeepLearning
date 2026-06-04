import pandas as pd
import re
from utils.preprocess import clean_text


def _extract_body_from_raw(raw_message):
    """Trích xuất body từ raw email, bỏ header và quoted messages."""
    if not isinstance(raw_message, str):
        return ""

    parts = raw_message.split("\n\n", 1)
    body = parts[1] if len(parts) > 1 else raw_message

    body = re.sub(r'-{3,}\s*Original Message\s*-{3,}.*', '', body, flags=re.DOTALL)
    body = re.sub(r'-{3,}\s*Forwarded.*?-{3,}', '', body, flags=re.DOTALL)

    return body.strip()


def _extract_subject_from_raw(raw_message):
    """Trích xuất Subject từ raw email header."""
    if not isinstance(raw_message, str):
        return ""
    match = re.search(r'^Subject:\s*(.*)$', raw_message, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _is_raw_email(text):
    """Kiểm tra text có phải raw email (chứa header) không."""
    if not isinstance(text, str) or len(text) < 50:
        return False
    headers = ['From:', 'Return-Path:', 'Received:', 'Date:', 'Subject:', 'To:',
               'Content-Type:', 'MIME-Version:', 'Delivered-To:']
    header_count = sum(1 for h in headers if h in text[:500])
    return header_count >= 2


def load_and_clean(path, encoding='latin-1'):
    """
    Load dataset SpamAssassin CSV và thực hiện cleaning.
    Yêu cầu: cột 'text' (nội dung email) + 'target' (nhãn ham/spam).
    """
    df = pd.read_csv(path, encoding=encoding)
    print(f"Raw dataset: {len(df)} rows, columns: {list(df.columns)}")

    # Lấy cột text + target từ SpamAssassin
    df = df[['text', 'target']].copy()
    df.columns = ['text', 'label']

    # Chuyển label text → số: ham=0, spam=1
    label_map = {'ham': 0, 'spam': 1}
    df['label'] = df['label'].str.lower().str.strip().map(label_map)
    df = df.dropna(subset=['label'])
    df['label'] = df['label'].astype(int)

    print(f"Label distribution (raw):\n{df['label'].value_counts().to_string()}")

    # Trích xuất subject + body nếu email chứa raw header
    sample_text = str(df['text'].iloc[0]) if len(df) > 0 else ""
    if _is_raw_email(sample_text):
        print("Raw email detected → extracting subject + body...")
        df['subject'] = df['text'].apply(_extract_subject_from_raw)
        df['body'] = df['text'].apply(_extract_body_from_raw)
        df['text'] = df['subject'] + " " + df['body']
        df = df.drop(columns=['subject', 'body'])

    # Cleaning
    df = df[['text', 'label']]
    df = df.dropna()
    df = df.drop_duplicates(subset=['text'])

    print("Applying text preprocessing...")
    df['clean_text'] = df['text'].apply(clean_text)

    # Loại bỏ text quá ngắn sau khi clean
    df = df[df['clean_text'].str.len() > 10]

    print(f"Dataset size after clean: {len(df)}")
    print(f"Label distribution:\n{df['label'].value_counts().to_string()}")

    return df
