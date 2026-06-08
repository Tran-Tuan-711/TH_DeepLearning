import re
from rules.vietnam_spam_rules import (
    SPAM_KEYWORD_GROUPS,
    TRUSTED_DOMAINS,
    SUSPICIOUS_DOMAIN_PATTERNS,
    SUSPICIOUS_SENDER_PATTERNS,
    TRUSTED_SENDER_PATTERNS,
)


class PhishingRuleEngine:
    def __init__(self, spam_threshold=1.5):
        self.spam_threshold = spam_threshold
        self.keyword_groups = SPAM_KEYWORD_GROUPS
        self.trusted_domains = [d.lower() for d in TRUSTED_DOMAINS]
        self.suspicious_domain_patterns = [
            re.compile(p, re.IGNORECASE) for p in SUSPICIOUS_DOMAIN_PATTERNS
        ]
        self.suspicious_sender_patterns = [
            re.compile(p, re.IGNORECASE) for p in SUSPICIOUS_SENDER_PATTERNS
        ]
        self.trusted_sender_patterns = [
            re.compile(p, re.IGNORECASE) for p in TRUSTED_SENDER_PATTERNS
        ]

    def _extract_domain(self, email_address):
        """Trích xuất domain từ email address."""
        if not email_address or "@" not in email_address:
            return ""
        return email_address.split("@")[-1].strip().lower()

    def _check_trusted_domain(self, domain):
        """Kiểm tra domain có trong whitelist không."""
        if not domain:
            return False
        # Exact match
        if domain in self.trusted_domains:
            return True
        # Subdomain match (e.g. classroom.google.com matches google.com)
        for trusted in self.trusted_domains:
            if domain.endswith("." + trusted):
                return True
        return False

    def _check_trusted_sender(self, sender_email):
        """Kiểm tra sender email có khớp trusted pattern không."""
        if not sender_email:
            return False
        for pattern in self.trusted_sender_patterns:
            if pattern.match(sender_email):
                return True
        return False

    def _check_suspicious_domain(self, domain):
        """Kiểm tra domain có khớp suspicious pattern không."""
        if not domain:
            return False
        for pattern in self.suspicious_domain_patterns:
            if pattern.match(domain):
                return True
        return False

    def _check_suspicious_sender(self, sender_email):
        """Kiểm tra sender có khớp suspicious pattern không."""
        if not sender_email:
            return False
        for pattern in self.suspicious_sender_patterns:
            if pattern.match(sender_email):
                return True
        return False

    def _match_keywords(self, text):
        text_lower = text.lower()
        matched_groups = []
        total_score = 0.0

        for group_id, group_info in self.keyword_groups.items():
            matched_keywords = []
            for keyword in group_info["keywords"]:
                if keyword.lower() in text_lower:
                    matched_keywords.append(keyword)

            if matched_keywords:
                group_score = group_info["weight"] * len(matched_keywords)
                total_score += group_score
                matched_groups.append({
                    "group_id": group_id,
                    "group_name": group_info["name"],
                    "matched_keywords": matched_keywords,
                    "weight": group_info["weight"],
                    "group_score": group_score,
                })

        return matched_groups, total_score

    def classify(self, subject="", body="", sender_email=""):
        full_text = f"{subject} {body}".strip()
        domain = self._extract_domain(sender_email)

        result = {
            "label": None,
            "confidence": 0.0,
            "method": None,
            "matched_rules": [],
            "spam_score": 0.0,
            "details": "",
        }

        # ─── STEP 1: Trusted sender pattern (email dịch vụ chính thức) ──
        # Chỉ các email official (noreply@github.com, *@*.google.com...)
        # mới được return Normal ngay — vì pattern này rất cụ thể
        if self._check_trusted_sender(sender_email):
            result["label"] = "Normal"
            result["confidence"] = 0.90
            result["method"] = "rule_whitelist"
            result["details"] = f"Sender '{sender_email}' khớp pattern email dịch vụ chính thức."
            return result

        # ─── STEP 2: Thu thập tín hiệu đáng ngờ ────────────────────────
        spam_score = 0.0
        is_trusted_domain = self._check_trusted_domain(domain)

        # Check suspicious domain
        if self._check_suspicious_domain(domain):
            spam_score += 1.0
            result["matched_rules"].append({
                "group_id": "suspicious_domain",
                "group_name": "Domain đáng ngờ",
                "matched_keywords": [domain],
                "weight": 1.0,
                "group_score": 1.0,
            })

        # ─── STEP 3: Keyword matching ─────────────────────────────────
        matched_groups, keyword_score = self._match_keywords(full_text)
        spam_score += keyword_score
        result["matched_rules"].extend(matched_groups)

        # ─── STEP 4: Suspicious sender check ──────────────────────────
        if self._check_suspicious_sender(sender_email):
            spam_score += 1.5
            result["matched_rules"].append({
                "group_id": "suspicious_sender",
                "group_name": "Tên email đáng ngờ",
                "matched_keywords": [sender_email],
                "weight": 1.5,
                "group_score": 1.5,
            })

        result["spam_score"] = spam_score

        # ─── STEP 5: Quyết định dựa trên score + trust ────────────────
        if spam_score >= self.spam_threshold:
            result["label"] = "Spam"
            result["confidence"] = min(0.99, 0.7 + spam_score * 0.05)
            result["method"] = "rule_keyword"

            group_names = [g["group_name"] for g in result["matched_rules"]]
            result["details"] = (
                f"Spam score: {spam_score:.1f} (threshold: {self.spam_threshold}). "
                f"Nhóm vi phạm: {', '.join(group_names)}"
            )
            return result

        # ─── STEP 6: Trusted domain + không có tín hiệu đáng ngờ → Normal
        if is_trusted_domain and spam_score == 0.0:
            result["label"] = "Normal"
            result["confidence"] = 0.92
            result["method"] = "rule_whitelist"
            result["details"] = (
                f"Domain '{domain}' nằm trong whitelist và không phát hiện "
                f"keyword/domain/sender đáng ngờ."
            )
            return result

        # ─── STEP 7: Không đủ evidence → fallback sang model ─────────
        trust_note = f" (domain '{domain}' thuộc whitelist nhưng có tín hiệu đáng ngờ)" if is_trusted_domain else ""
        result["label"] = None
        result["details"] = (
            f"Spam score: {spam_score:.1f} (dưới threshold {self.spam_threshold}){trust_note}. "
            f"Cần model AI để phân loại."
        )
        return result


# Singleton instance cho sử dụng nhanh
_engine = None


def get_engine(spam_threshold=1.5):
    """Lấy singleton instance của PhishingRuleEngine."""
    global _engine
    if _engine is None:
        _engine = PhishingRuleEngine(spam_threshold=spam_threshold)
    return _engine
