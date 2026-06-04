import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
import re
from datetime import datetime



def detect_imap_server(email_addr):
    if not email_addr or "@" not in email_addr:
        return None, None, None

    domain = email_addr.split("@")[-1].strip().lower()

    DOMAIN_MAP = {
        "gmail.com": ("imap.gmail.com", 993, "Gmail"),
        "googlemail.com": ("imap.gmail.com", 993, "Gmail"),
        "outlook.com": ("outlook.office365.com", 993, "Outlook"),
        "hotmail.com": ("outlook.office365.com", 993, "Outlook"),
        "live.com": ("outlook.office365.com", 993, "Outlook"),
        "msn.com": ("outlook.office365.com", 993, "Outlook"),
        "yahoo.com": ("imap.mail.yahoo.com", 993, "Yahoo Mail"),
        "yahoo.co.jp": ("imap.mail.yahoo.co.jp", 993, "Yahoo Mail JP"),
        "ymail.com": ("imap.mail.yahoo.com", 993, "Yahoo Mail"),
        "icloud.com": ("imap.mail.me.com", 993, "iCloud Mail"),
        "me.com": ("imap.mail.me.com", 993, "iCloud Mail"),
        "mac.com": ("imap.mail.me.com", 993, "iCloud Mail"),
        "zoho.com": ("imap.zoho.com", 993, "Zoho Mail"),
        "protonmail.com": ("127.0.0.1", 1143, "ProtonMail (Bridge)"),
        "aol.com": ("imap.aol.com", 993, "AOL Mail"),
    }

    if domain in DOMAIN_MAP:
        return DOMAIN_MAP[domain]

    # Fallback: thử imap.<domain>
    return f"imap.{domain}", 993, domain.capitalize()


class IMAPEmailReader:
    def __init__(self):
        self.connection = None
        self.is_connected = False

    def connect(self, server, port, email_addr, password):
        try:
            self.connection = imaplib.IMAP4_SSL(server, port)
            self.connection.login(email_addr, password)
            self.is_connected = True
        except imaplib.IMAP4.error as e:
            self.is_connected = False
            error_msg = str(e)
            if "AUTHENTICATIONFAILED" in error_msg.upper() or "LOGIN" in error_msg.upper():
                raise AuthenticationError(
                    f"Sai email hoặc mật khẩu. "
                    f"Nếu dùng Gmail, hãy tạo App Password tại: "
                    f"https://myaccount.google.com/apppasswords"
                ) from e
            raise ConnectionError(f"Không thể kết nối đến {server}:{port} — {error_msg}") from e
        except Exception as e:
            self.is_connected = False
            raise ConnectionError(f"Lỗi kết nối: {e}") from e

    def fetch_emails(self, folder="INBOX", limit=20):
        if not self.is_connected or self.connection is None:
            raise ConnectionError("Chưa kết nối IMAP. Gọi connect() trước.")

        # Select folder
        status, _ = self.connection.select(folder, readonly=True)
        if status != "OK":
            raise ConnectionError(f"Không thể mở folder '{folder}'")

        # Search all emails
        status, message_ids = self.connection.search(None, "ALL")
        if status != "OK":
            return []

        id_list = message_ids[0].split()
        if not id_list:
            return []

        # Lấy N email mới nhất (cuối danh sách)
        recent_ids = id_list[-limit:]
        recent_ids.reverse()  # Mới nhất trước

        emails = []
        for msg_id in recent_ids:
            try:
                email_data = self._fetch_single(msg_id)
                if email_data:
                    emails.append(email_data)
            except Exception:
                # Skip email bị lỗi parse
                continue

        return emails


    def disconnect(self):
        """Đóng kết nối IMAP."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            try:
                self.connection.logout()
            except Exception:
                pass
        self.connection = None
        self.is_connected = False

    # ─── Private methods ───────────────────────────────────────────────

    def _fetch_single(self, msg_id):
        """Fetch và parse một email theo ID."""
        status, data = self.connection.fetch(msg_id, "(RFC822)")
        if status != "OK" or not data or not data[0]:
            return None

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Parse sender
        sender_raw = msg.get("From", "")
        sender_name, sender_email = parseaddr(sender_raw)
        sender_name = self._decode_header_value(sender_name) or sender_email

        # Parse subject
        subject = self._decode_header_value(msg.get("Subject", ""))

        # Parse date
        date_obj = None
        date_str = ""
        raw_date = msg.get("Date", "")
        if raw_date:
            try:
                date_obj = parsedate_to_datetime(raw_date)
                date_str = date_obj.strftime("%d/%m/%Y %H:%M")
            except Exception:
                date_str = raw_date[:25]

        # Parse body (plain text)
        body = self._extract_body(msg)

        # Message ID
        message_id = msg.get("Message-ID", str(msg_id))

        return {
            "message_id": message_id,
            "sender": sender_email,
            "sender_name": sender_name,
            "subject": subject,
            "body": body,
            "date": date_obj,
            "date_str": date_str,
        }

    def _decode_header_value(self, value):
        """Decode header value (xử lý encoded headers như =?UTF-8?B?...)."""
        if not value:
            return ""
        try:
            decoded_parts = decode_header(value)
            result = []
            for part, charset in decoded_parts:
                if isinstance(part, bytes):
                    charset = charset or "utf-8"
                    try:
                        result.append(part.decode(charset, errors="replace"))
                    except (LookupError, UnicodeDecodeError):
                        result.append(part.decode("utf-8", errors="replace"))
                else:
                    result.append(str(part))
            return " ".join(result).strip()
        except Exception:
            return str(value)

    def _extract_body(self, msg):
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        try:
                            body = payload.decode(charset, errors="replace")
                        except (LookupError, UnicodeDecodeError):
                            body = payload.decode("utf-8", errors="replace")
                        break  # Lấy text/plain đầu tiên

            # Fallback: nếu không có text/plain, thử text/html
            if not body.strip():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or "utf-8"
                            try:
                                html = payload.decode(charset, errors="replace")
                            except (LookupError, UnicodeDecodeError):
                                html = payload.decode("utf-8", errors="replace")
                            body = self._html_to_text(html)
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                try:
                    body = payload.decode(charset, errors="replace")
                except (LookupError, UnicodeDecodeError):
                    body = payload.decode("utf-8", errors="replace")

                # Nếu content type là HTML → strip tags
                if msg.get_content_type() == "text/html":
                    body = self._html_to_text(body)

        return body.strip()

    @staticmethod
    def _html_to_text(html):
        """Chuyển HTML sang plain text (đơn giản)."""
        # Remove style, script tags
        text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Replace br, p tags with newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&quot;', '"', text)
        # Clean up whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


class AuthenticationError(Exception):
    """Lỗi xác thực IMAP (sai email/password)."""
    pass
