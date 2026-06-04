# 📧 Email Spam Classification — Deep Learning + Rule-based

Hệ thống phân loại email **Spam / Normal** sử dụng kết hợp **mô hình CNN (Deep Learning)** và **bộ luật phát hiện spam/phishing (Rule-based)**, hỗ trợ cả email **tiếng Anh** và **tiếng Việt**.

Tích hợp **giao diện đồ họa (GUI)** cho phép phân loại email thủ công hoặc **đọc trực tiếp từ hộp thư IMAP** (Gmail, Outlook, Yahoo...).

---

## 🎯 Mục Tiêu

- Phân loại email thành **Spam** hoặc **Normal (Ham)** với độ chính xác cao
- Hỗ trợ email **song ngữ** (Tiếng Anh + Tiếng Việt)
- Kết hợp 2 phương pháp:
  - **Rule-based Engine** — phát hiện spam tiếng Việt bằng bộ từ khóa + luật (nhanh, chính xác)
  - **CNN model** — train trên dataset SpamAssassin (tiếng Anh), xử lý các trường hợp phức tạp
- **Giao diện GUI** trực quan, hỗ trợ đọc email từ IMAP server

---

## 🏗️ Kiến Trúc Hệ Thống

```
                    ┌──────────────┐
                    │  Email Input  │
                    │ (GUI / IMAP)  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Rule Engine  │──── Whitelist? ──→ ✅ Normal
                    │ (Luật VN+EN) │──── Spam Score ≥ Threshold? ──→ 🚫 Spam
                    └──────┬───────┘
                           │ (Không quyết định được)
                    ┌──────▼───────┐
                    │  CNN Model   │──── Probability > 0.5 ──→ 🚫 Spam
                    │(SpamAssassin)│──── Probability ≤ 0.5 ──→ ✅ Normal
                    └──────────────┘
```

### Quy trình phân loại:
1. **Rule-based check (ưu tiên):** Kiểm tra domain đáng tin cậy (whitelist), domain đáng ngờ, từ khóa spam VN theo 6 nhóm, pattern sender đáng ngờ
2. **CNN model (fallback):** Nếu rule không đủ chứng cứ → sử dụng mô hình CNN (train trên SpamAssassin) để phân loại

---

## 📂 Cấu Trúc Dự Án

```
TH_DeepLearning/
├── GUI/                           # Giao diện đồ họa (GUI Desktop)
│   ├── __init__.py
│   ├── app.py                     # Ứng dụng GUI chính (tkinter)
│   └── imap_reader.py             # Module đọc email từ IMAP server
│
├── data/                          # Dataset phục vụ huấn luyện & đánh giá
│   ├── spam_assassin.csv          # Dataset gốc SpamAssassin (tiếng Anh, raw)
│   └── spam_clean.csv             # Dataset SpamAssassin đã clean — dùng để train CNN
│
├── model/                         # Mô hình Deep Learning (CNN)
│   ├── train_cnn.py               # Huấn luyện mô hình CNN trên SpamAssassin
│   └── predict_cnn.py             # Dự đoán / Phân loại email mới
│
├── rules/                         # Bộ luật phát hiện spam/phishing (VN + EN)
│   ├── __init__.py
│   ├── rule_engine.py             # Engine xử lý luật (PhishingRuleEngine)
│   └── vietnam_spam_rules.py      # Từ khóa & rules cho email Việt Nam
│
├── utils/                         # Tiện ích dùng chung
│   ├── __init__.py
│   ├── clean_dataset.py           # Làm sạch dataset (hỗ trợ nhiều format)
│   ├── preprocess.py              # Tiền xử lý văn bản (EN & VN)
│   ├── logger.py                  # Cấu hình logging
│   └── save_clean_data.py         # Lưu dataset đã clean
│
├── main.py                        # Entry point — chạy GUI application
├── test.py                        # Test cases phân loại email
├── requirements.txt               # Thư viện Python cần cài đặt
├── PROJECT_STRUCTURE.md            # Tài liệu chi tiết cấu trúc dự án
└── README.md                      # File này
```

> 📝 Xem chi tiết ý nghĩa từng file/folder trong [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## ⚙️ Cài Đặt

### 1. Yêu cầu hệ thống
- **Python** >= 3.9
- **pip** (Python package manager)
- **tkinter** (thường đi kèm Python, không cần cài riêng)
- (Khuyến nghị) GPU hỗ trợ CUDA để tăng tốc huấn luyện

### 2. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 3. Tải NLTK data (lần đầu)

```python
import nltk
nltk.download('stopwords')
```

---

## 🚀 Hướng Dẫn Sử Dụng

### ▶️ Chạy ứng dụng GUI (khuyến nghị)

```bash
python main.py
```

Giao diện GUI sẽ mở ra với 2 tab:

#### Tab 1 — Phân loại thủ công
- Nhập **email người gửi**, **tiêu đề**, **nội dung** email
- Nhấn **"🔍 Phân loại"** để xem kết quả
- Hiển thị: Nhãn (Spam/Normal), độ tin cậy, phương pháp phân loại, chi tiết rules

#### Tab 2 — Đọc email từ IMAP
- Chọn preset (Gmail/Outlook/Yahoo) hoặc nhập thông tin IMAP server
- Nhập email và mật khẩu (App Password cho Gmail)
- Nhấn **"📥 Kết nối & Đọc email"** để tự động fetch và phân loại
- Danh sách email hiển thị trong bảng với màu: 🟢 Normal / 🔴 Spam
- Click vào email để xem chi tiết nội dung + kết quả phân loại

### 📧 Cấu hình đọc email IMAP

| Dịch vụ | IMAP Server | Port | Ghi chú |
|---------|-------------|------|---------|
| **Gmail** | `imap.gmail.com` | 993 | Cần tạo **App Password** |
| **Outlook** | `outlook.office365.com` | 993 | Dùng mật khẩu thường |
| **Yahoo** | `imap.mail.yahoo.com` | 993 | Cần tạo App Password |

> ⚠️ **Gmail App Password:** Gmail không cho phép đăng nhập bằng mật khẩu thường qua IMAP. Bạn cần:
> 1. Bật **2-Step Verification** tại [myaccount.google.com](https://myaccount.google.com)
> 2. Tạo **App Password** tại [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
> 3. Sử dụng App Password (16 ký tự) thay cho mật khẩu thường

---

### 🔧 Pipeline huấn luyện (dành cho developer)

#### Bước 1: Làm sạch dataset SpamAssassin (chạy 1 lần)

```bash
python -m utils.save_clean_data
```

Kết quả: `data/spam_clean.csv` (dataset SpamAssassin đã clean)

#### Bước 2: Huấn luyện mô hình CNN

```bash
python -m model.train_cnn
```

Kết quả sau khi train:
- Model: `model/cnn_model.h5`
- Tokenizer: `model/tokenizer.pkl`
- Biểu đồ: `logs/charts/training_history.png`
- Log: `logs/train.log`

---

## 🖥️ Giao Diện GUI

### Tính năng chính

| Tính năng | Mô tả |
|-----------|-------|
| **Phân loại thủ công** | Nhập email → phân loại ngay lập tức |
| **Đọc IMAP** | Kết nối hộp thư → fetch & phân loại hàng loạt |
| **Dark theme** | Giao diện tối, dễ nhìn, chuyên nghiệp |
| **Hiển thị chi tiết** | Xem method, confidence, matched rules, spam score |
| **Non-blocking** | Threading — GUI không bị đơ khi xử lý |
| **Preset servers** | Nút nhanh cho Gmail, Outlook, Yahoo |

---

## 🧠 Mô Hình CNN

### Dataset huấn luyện

| Dataset | Ngôn ngữ | Kích thước | Nguồn |
|---------|----------|------------|-------|
| **SpamAssassin** | Tiếng Anh | ~24MB (raw) | [SpamAssassin Public Corpus](https://spamassassin.apache.org/) |

> 💡 CNN model train trên SpamAssassin (EN). Email tiếng Việt được xử lý ưu tiên bởi Rule Engine trước khi đến CNN.

### Kiến trúc CNN

| Layer | Chi tiết |
|-------|----------|
| **Embedding** | `num_words=10000`, `embedding_dim=128`, `input_length=200` |
| **Conv1D** | `filters=128`, `kernel_size=5`, `activation='relu'` |
| **GlobalMaxPooling1D** | Lấy đặc trưng quan trọng nhất |
| **Dense** | `units=64`, `activation='relu'` |
| **Dropout** | `rate=0.5` (chống overfitting) |
| **Dense (output)** | `units=1`, `activation='sigmoid'` (binary classification) |

### Hyperparameters

| Parameter | Giá trị |
|-----------|---------|
| Max Words (vocab size) | 10,000 |
| Max Sequence Length | 200 |
| Batch Size | 32 |
| Epochs | 10 (với EarlyStopping patience=3) |
| Optimizer | Adam |
| Loss Function | Binary Crossentropy |
| Train/Test Split | 80/20 |

---

## 📏 Rule-based Engine

Hệ thống luật phát hiện spam gồm **6 nhóm từ khóa tiếng Việt** với trọng số khác nhau:

| Nhóm | Trọng số | Mô tả |
|------|----------|-------|
| 🏦 Giả mạo ngân hàng | 2.0 | Giả mạo VCB, Techcombank, MoMo, ZaloPay... |
| 💰 Tiền bạc / Khuyến mãi | 1.5 | Trúng thưởng, giảm giá sốc, ưu đãi... |
| 🔐 Giả mạo dịch vụ | 1.8 | Fake urgency, fake link, fake security... |
| 📈 Lừa đảo đầu tư | 1.7 | Bitcoin, crypto, forex, lợi nhuận cam kết... |
| 💼 Việc làm giả | 1.3 | Việc nhẹ lương cao, tuyển CTV online... |
| 🔔 Thông báo giả | 1.2 | Bưu phẩm chưa nhận, trúng thưởng Shopee... |

**Ngưỡng spam:** `spam_score ≥ 1.5` → phân loại Spam bằng rule

> 💡 Rule Engine xử lý ưu tiên email VN. Nếu rule không đủ chứng cứ → fallback sang CNN model.

---

## 🛠️ Công Nghệ Sử Dụng

| Công nghệ | Vai trò |
|------------|---------|
| **TensorFlow / Keras** | Xây dựng và huấn luyện mô hình CNN |
| **NLTK** | Xử lý ngôn ngữ tự nhiên (stopwords, stemming) |
| **scikit-learn** | Chia train/test, đánh giá (classification report, confusion matrix) |
| **Pandas** | Xử lý dữ liệu dạng bảng (DataFrame) |
| **NumPy** | Tính toán ma trận / mảng số |
| **Matplotlib** | Vẽ biểu đồ training (loss, accuracy) |
| **tkinter** | Giao diện đồ họa desktop (GUI) |
| **imaplib** | Đọc email từ IMAP server |

---

## 📈 Monitoring

- **TensorBoard:** Log được lưu tại `logs/fit/` — chạy `tensorboard --logdir logs/fit` để theo dõi trực quan
- **Training charts:** Biểu đồ loss/accuracy lưu tại `logs/charts/training_history.png`
- **Log file:** `logs/train.log` — ghi lại toàn bộ quá trình huấn luyện

---

## 🔄 Luồng Hoạt Động (Pipeline)

```
1. Clean dataset EN          →  utils/save_clean_data.py  → spam_clean.csv
2. Huấn luyện CNN            →  model/train_cnn.py        → cnn_model.h5 + tokenizer.pkl
3. Chạy GUI                  →  python main.py            → Giao diện phân loại email
   ├── Tab 1: Nhập thủ công  →  Nhập email → Phân loại
   ├── Tab 2: Đọc IMAP       →  GUI/imap_reader.py        → Fetch & phân loại hàng loạt
   ├── Rule Engine (VN)       →  rules/rule_engine.py      → Check whitelist + keywords VN
   └── CNN model (EN)         →  model/predict_cnn.py      → Fallback nếu rule không quyết định
```

---

## 📝 Ghi Chú

- Chạy `python main.py` để mở giao diện GUI phân loại email
- CNN model train trên **SpamAssassin** (tiếng Anh) — xử lý tốt email EN
- Rule Engine xử lý **email tiếng Việt** bằng bộ từ khóa 6 nhóm — không cần train
- Kết hợp cả hai: Rule check trước → CNN fallback → kết quả chính xác cho cả EN và VN
- GUI sử dụng **100% thư viện built-in** Python (tkinter, imaplib, email) — không cần cài thêm
