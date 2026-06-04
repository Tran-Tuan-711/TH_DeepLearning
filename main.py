"""
Entry point — Chạy GUI Email Spam Classifier.
Usage: python main.py
"""

import sys
import os

# Đảm bảo import path đúng
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import EmailClassifierApp


def main():
    app = EmailClassifierApp()
    app.run()


if __name__ == "__main__":
    main()