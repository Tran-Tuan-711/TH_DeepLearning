import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── Color Palette ──────────────────────────────────────────────────
C = {
    "bg": "#0f0f1a", "surface": "#1a1a2e", "card": "#16213e",
    "accent": "#0f3460", "primary": "#533483", "highlight": "#e94560",
    "success": "#00d2a0", "danger": "#ff4757", "warning": "#ffa502",
    "text": "#eaecef", "text2": "#8b95a5", "border": "#2a2a4a",
    "input_bg": "#0d1117", "btn_hover": "#6c44a2",
}

FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
FONT_H = ("Segoe UI", 16, "bold")
FONT_S = ("Segoe UI", 9)


class EmailClassifierApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📧 Email Spam Classifier — Deep Learning + Rule-based")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        self.root.configure(bg=C["bg"])
        self._configure_styles()
        self._build_ui()
        self.imap_emails = []

    def run(self):
        self.root.mainloop()

    # ─── Styles ─────────────────────────────────────────────────────
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=C["bg"], foreground=C["text"], font=FONT)
        style.configure("TFrame", background=C["bg"])
        style.configure("Card.TFrame", background=C["card"])
        style.configure("TLabel", background=C["bg"], foreground=C["text"], font=FONT)
        style.configure("Card.TLabel", background=C["card"])
        style.configure("Header.TLabel", font=FONT_H, foreground=C["highlight"])
        style.configure("Sub.TLabel", font=FONT_S, foreground=C["text2"])
        style.configure("Success.TLabel", foreground=C["success"], font=("Segoe UI", 14, "bold"))
        style.configure("Danger.TLabel", foreground=C["danger"], font=("Segoe UI", 14, "bold"))
        style.configure("TNotebook", background=C["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=C["surface"], foreground=C["text"],
                        padding=[18, 8], font=FONT_B)
        style.map("TNotebook.Tab", background=[("selected", C["primary"])],
                  foreground=[("selected", "#ffffff")])
        style.configure("Accent.TButton", background=C["primary"], foreground="#fff",
                        font=FONT_B, padding=[20, 10])
        style.map("Accent.TButton", background=[("active", C["btn_hover"])])
        style.configure("TEntry", fieldbackground=C["input_bg"], foreground=C["text"],
                        insertcolor=C["text"], borderwidth=1)
        style.configure("Treeview", background=C["surface"], foreground=C["text"],
                        fieldbackground=C["surface"], rowheight=28, font=FONT_S)
        style.configure("Treeview.Heading", background=C["accent"], foreground="#fff",
                        font=FONT_B)
        style.map("Treeview", background=[("selected", C["primary"])])

    # ─── Build UI ───────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = ttk.Frame(self.root)
        hdr.pack(fill="x", padx=20, pady=(15, 5))
        ttk.Label(hdr, text="📧 Email Spam Classifier", style="Header.TLabel").pack(side="left")
        ttk.Label(hdr, text="Deep Learning (CNN) + Rule-based Engine",
                  style="Sub.TLabel").pack(side="left", padx=(12, 0), pady=(5, 0))

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        self._build_manual_tab()
        self._build_imap_tab()

        # Status bar
        self.status_var = tk.StringVar(value="✅ Sẵn sàng")
        sb = ttk.Label(self.root, textvariable=self.status_var, style="Sub.TLabel")
        sb.pack(fill="x", padx=20, pady=(0, 8))

    # ─── Tab 1: Manual Classification ──────────────────────────────
    def _build_manual_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  ✍ Phân loại thủ công  ")

        # Left panel - input
        left = ttk.Frame(tab)
        left.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

        # Sender
        ttk.Label(left, text="📬 Email người gửi:", style="Card.TLabel").pack(anchor="w", pady=(0, 3))
        self.sender_var = tk.StringVar()
        e = tk.Entry(left, textvariable=self.sender_var, font=FONT,
                     bg=C["input_bg"], fg=C["text"], insertbackground=C["text"],
                     relief="flat", bd=0, highlightthickness=1,
                     highlightbackground=C["border"], highlightcolor=C["primary"])
        e.pack(fill="x", pady=(0, 10), ipady=6)

        # Subject
        ttk.Label(left, text="📝 Tiêu đề (Subject):", style="Card.TLabel").pack(anchor="w", pady=(0, 3))
        self.subject_var = tk.StringVar()
        e2 = tk.Entry(left, textvariable=self.subject_var, font=FONT,
                      bg=C["input_bg"], fg=C["text"], insertbackground=C["text"],
                      relief="flat", bd=0, highlightthickness=1,
                      highlightbackground=C["border"], highlightcolor=C["primary"])
        e2.pack(fill="x", pady=(0, 10), ipady=6)

        # Body
        ttk.Label(left, text="📄 Nội dung email:", style="Card.TLabel").pack(anchor="w", pady=(0, 3))
        self.body_text = scrolledtext.ScrolledText(
            left, font=FONT, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["text"], relief="flat", bd=0,
            highlightthickness=1, highlightbackground=C["border"],
            highlightcolor=C["primary"], height=10, wrap="word")
        self.body_text.pack(fill="both", expand=True, pady=(0, 10))

        # Button
        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill="x")
        self.classify_btn = tk.Button(
            btn_frame, text="🔍  PHÂN LOẠI EMAIL", font=FONT_B,
            bg=C["primary"], fg="#fff", activebackground=C["btn_hover"],
            activeforeground="#fff", relief="flat", cursor="hand2",
            bd=0, padx=20, pady=10, command=self._on_classify)
        self.classify_btn.pack(fill="x", ipady=2)

        clear_btn = tk.Button(
            btn_frame, text="🗑  Xóa", font=FONT_S,
            bg=C["surface"], fg=C["text2"], activebackground=C["card"],
            relief="flat", bd=0, cursor="hand2", command=self._on_clear_manual)
        clear_btn.pack(fill="x", pady=(5, 0), ipady=2)

        # Right panel - result
        right = ttk.Frame(tab)
        right.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        ttk.Label(right, text="📊 Kết quả phân loại", style="Header.TLabel",
                  font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 10))

        self.result_frame = tk.Frame(right, bg=C["card"], highlightthickness=1,
                                     highlightbackground=C["border"])
        self.result_frame.pack(fill="both", expand=True)

        self.result_label_var = tk.StringVar(value="—")
        self.result_conf_var = tk.StringVar(value="")
        self.result_method_var = tk.StringVar(value="")

        self.result_icon = tk.Label(self.result_frame, text="📧", font=("Segoe UI", 48),
                                    bg=C["card"], fg=C["text2"])
        self.result_icon.pack(pady=(30, 5))

        self.result_label = tk.Label(self.result_frame, textvariable=self.result_label_var,
                                     font=("Segoe UI", 22, "bold"), bg=C["card"], fg=C["text2"])
        self.result_label.pack()

        self.result_conf = tk.Label(self.result_frame, textvariable=self.result_conf_var,
                                    font=("Segoe UI", 12), bg=C["card"], fg=C["text2"])
        self.result_conf.pack(pady=(5, 0))

        self.result_method = tk.Label(self.result_frame, textvariable=self.result_method_var,
                                      font=FONT_S, bg=C["card"], fg=C["text2"])
        self.result_method.pack(pady=(3, 0))

        self.result_details = scrolledtext.ScrolledText(
            self.result_frame, font=FONT_S, bg=C["input_bg"], fg=C["text2"],
            relief="flat", height=8, wrap="word", state="disabled",
            highlightthickness=0)
        self.result_details.pack(fill="both", expand=True, padx=10, pady=10)

    # ─── Tab 2: IMAP Reader ────────────────────────────────────────
    def _build_imap_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  📥 Đọc email từ IMAP  ")

        # Top - connection form
        conn_frame = tk.Frame(tab, bg=C["card"], highlightthickness=1,
                               highlightbackground=C["border"])
        conn_frame.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(conn_frame, text="🔗 Kết nối Email", style="Card.TLabel",
                  font=FONT_B, background=C["card"]).grid(row=0, column=0, columnspan=4,
                                                           sticky="w", padx=10, pady=(8, 5))

        # Row 1: Email
        ttk.Label(conn_frame, text="📧 Email:", background=C["card"],
                  font=FONT_S).grid(row=1, column=0, sticky="w", padx=(10, 3), pady=3)
        self.imap_email_var = tk.StringVar()
        self.imap_email_var.trace_add("write", self._on_email_changed)
        email_entry = tk.Entry(conn_frame, textvariable=self.imap_email_var, font=FONT,
                     bg=C["input_bg"], fg=C["text"], insertbackground=C["text"],
                     relief="flat", highlightthickness=1,
                     highlightbackground=C["border"], highlightcolor=C["primary"],
                     width=35)
        email_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=3, ipady=4)

        # Server info label (auto-detected, shown on the right of email row)
        self.server_info_var = tk.StringVar(value="")
        self.server_info_label = tk.Label(conn_frame, textvariable=self.server_info_var,
                                          font=FONT_S, bg=C["card"], fg=C["text2"],
                                          anchor="w")
        self.server_info_label.grid(row=1, column=2, columnspan=2, sticky="w", padx=(5, 10), pady=3)

        # Row 2: App Password
        ttk.Label(conn_frame, text="🔑 App Password:", background=C["card"],
                  font=FONT_S).grid(row=2, column=0, sticky="w", padx=(10, 3), pady=3)
        self.imap_password_var = tk.StringVar()
        tk.Entry(conn_frame, textvariable=self.imap_password_var, font=FONT, show="*",
                 bg=C["input_bg"], fg=C["text"], insertbackground=C["text"],
                 relief="flat", highlightthickness=1,
                 highlightbackground=C["border"], highlightcolor=C["primary"],
                 width=35).grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=3, ipady=4)

        # Row 2 right: Số email
        ttk.Label(conn_frame, text="📊 Số email:", background=C["card"],
                  font=FONT_S).grid(row=2, column=2, sticky="w", padx=(5, 3), pady=3)
        self.limit_var = tk.StringVar(value="20")
        tk.Entry(conn_frame, textvariable=self.limit_var, font=FONT, width=6,
                 bg=C["input_bg"], fg=C["text"], insertbackground=C["text"],
                 relief="flat", highlightthickness=1,
                 highlightbackground=C["border"]).grid(row=2, column=3, sticky="w",
                                                        padx=(0, 10), pady=3, ipady=4)

        # Connect button
        btn_f = tk.Frame(conn_frame, bg=C["card"])
        btn_f.grid(row=3, column=0, columnspan=4, sticky="ew", padx=10, pady=(5, 10))
        self.connect_btn = tk.Button(
            btn_f, text="📥  KẾT NỐI & ĐỌC EMAIL", font=FONT_B,
            bg=C["primary"], fg="#fff", activebackground=C["btn_hover"],
            relief="flat", bd=0, cursor="hand2", padx=20, pady=8,
            command=self._on_connect_imap)
        self.connect_btn.pack(fill="x", ipady=2)

        conn_frame.columnconfigure(1, weight=1)

        # Bottom - email list + detail
        bottom = ttk.Frame(tab)
        bottom.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Email list (left)
        list_frame = ttk.Frame(bottom)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        cols = ("sender", "subject", "date", "label", "confidence")
        self.email_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=12)
        self.email_tree.heading("sender", text="Người gửi")
        self.email_tree.heading("subject", text="Tiêu đề")
        self.email_tree.heading("date", text="Ngày")
        self.email_tree.heading("label", text="Nhãn")
        self.email_tree.heading("confidence", text="Conf%")
        self.email_tree.column("sender", width=160)
        self.email_tree.column("subject", width=220)
        self.email_tree.column("date", width=110)
        self.email_tree.column("label", width=70, anchor="center")
        self.email_tree.column("confidence", width=60, anchor="center")

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.email_tree.yview)
        self.email_tree.configure(yscrollcommand=sb.set)
        self.email_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.email_tree.bind("<<TreeviewSelect>>", self._on_email_select)

        # Detail panel (right)
        detail = tk.Frame(bottom, bg=C["card"], highlightthickness=1,
                          highlightbackground=C["border"], width=320)
        detail.pack(side="right", fill="both", padx=(5, 0))
        detail.pack_propagate(False)

        ttk.Label(detail, text="📋 Chi tiết", background=C["card"],
                  font=FONT_B).pack(anchor="w", padx=10, pady=(8, 5))

        self.detail_text = scrolledtext.ScrolledText(
            detail, font=FONT_S, bg=C["input_bg"], fg=C["text"],
            relief="flat", wrap="word", state="disabled", highlightthickness=0)
        self.detail_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    # ─── Actions ────────────────────────────────────────────────────
    def _on_email_changed(self, *args):
        """Callback khi email thay đổi — tự động nhận diện IMAP server."""
        from GUI.imap_reader import detect_imap_server
        email_addr = self.imap_email_var.get().strip()
        server, port, display_name = detect_imap_server(email_addr)
        if server and display_name:
            self.server_info_var.set(f"🌐 {display_name}  ({server}:{port})")
            self.server_info_label.config(fg=C["success"])
        else:
            self.server_info_var.set("")

    def _on_classify(self):
        body = self.body_text.get("1.0", "end").strip()
        subject = self.subject_var.get().strip()
        sender = self.sender_var.get().strip()

        if not body and not subject:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập nội dung hoặc tiêu đề email.")
            return

        self.classify_btn.config(state="disabled", text="⏳ Đang phân loại...")
        self.status_var.set("⏳ Đang phân loại email...")

        def do_classify():
            try:
                from model.predict_cnn import predict_email
                full_text = f"{subject}\n{body}" if subject else body
                result = predict_email(text=full_text, sender_email=sender or None)
                self.root.after(0, lambda: self._show_result(result))
            except Exception as ex:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi phân loại:\n{ex}"))
            finally:
                self.root.after(0, lambda: self.classify_btn.config(
                    state="normal", text="🔍  PHÂN LOẠI EMAIL"))
                self.root.after(0, lambda: self.status_var.set("✅ Sẵn sàng"))

        threading.Thread(target=do_classify, daemon=True).start()

    def _show_result(self, result):
        label = result["label"]
        conf = result["confidence"]
        method = result.get("method", "")

        is_spam = label == "Spam"
        color = C["danger"] if is_spam else C["success"]
        icon = "🚫" if is_spam else "✅"

        self.result_icon.config(text=icon)
        self.result_label_var.set(label)
        self.result_label.config(fg=color)
        self.result_conf_var.set(f"Độ tin cậy: {conf:.1%}")
        self.result_conf.config(fg=color)

        method_map = {"rule_whitelist": "📋 Rule: Whitelist domain",
                      "rule_keyword": "📋 Rule: Keyword matching",
                      "model_cnn": "🧠 CNN Deep Learning model"}
        self.result_method_var.set(method_map.get(method, method))

        # Details
        details = f"Label: {label}\nConfidence: {conf:.1%}\nMethod: {method}\n"
        if result.get("spam_score"):
            details += f"Spam Score: {result['spam_score']}\n"
        if result.get("matched_rules"):
            details += "\n── Matched Rules ──\n"
            for r in result["matched_rules"]:
                details += f"  [{r['group_name']}] score={r['group_score']:.1f}\n"
                for kw in r.get("matched_keywords", [])[:5]:
                    details += f"    → {kw}\n"
        if result.get("details"):
            details += f"\n{result['details']}\n"

        self.result_details.config(state="normal")
        self.result_details.delete("1.0", "end")
        self.result_details.insert("1.0", details)
        self.result_details.config(state="disabled")

    def _on_clear_manual(self):
        self.sender_var.set("")
        self.subject_var.set("")
        self.body_text.delete("1.0", "end")
        self.result_label_var.set("—")
        self.result_conf_var.set("")
        self.result_method_var.set("")
        self.result_icon.config(text="📧")
        self.result_label.config(fg=C["text2"])
        self.result_details.config(state="normal")
        self.result_details.delete("1.0", "end")
        self.result_details.config(state="disabled")

    def _on_connect_imap(self):
        from GUI.imap_reader import detect_imap_server

        email_addr = self.imap_email_var.get().strip()
        password = self.imap_password_var.get().strip()

        if not email_addr or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập email và App Password.")
            return

        server, port, display_name = detect_imap_server(email_addr)
        if not server:
            messagebox.showerror("Lỗi", "Không thể nhận diện IMAP server từ email này.")
            return

        try:
            limit = int(self.limit_var.get())
        except ValueError:
            limit = 20

        self.connect_btn.config(state="disabled", text="⏳ Đang kết nối...")
        self.status_var.set(f"⏳ Đang kết nối đến {display_name} ({server})...")

        def do_fetch():
            try:
                from GUI.imap_reader import IMAPEmailReader
                reader = IMAPEmailReader()
                reader.connect(server, port, email_addr, password)
                emails = reader.fetch_emails(folder="INBOX", limit=limit)
                reader.disconnect()

                # Classify each email
                from model.predict_cnn import predict_email
                results = []
                for i, em in enumerate(emails):
                    self.root.after(0, lambda idx=i, total=len(emails):
                                   self.status_var.set(f"⏳ Phân loại {idx+1}/{total}..."))
                    full_text = f"{em['subject']}\n{em['body']}"
                    res = predict_email(text=full_text, sender_email=em["sender"] or None)
                    results.append({"email": em, "result": res})

                self.imap_emails = results
                self.root.after(0, lambda: self._populate_email_tree(results))
                self.root.after(0, lambda: self.status_var.set(
                    f"✅ Đã đọc và phân loại {len(results)} email"))
            except Exception as ex:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", str(ex)))
                self.root.after(0, lambda: self.status_var.set("❌ Lỗi kết nối"))
            finally:
                self.root.after(0, lambda: self.connect_btn.config(
                    state="normal", text="📥  KẾT NỐI & ĐỌC EMAIL"))

        threading.Thread(target=do_fetch, daemon=True).start()

    def _populate_email_tree(self, results):
        for item in self.email_tree.get_children():
            self.email_tree.delete(item)
        for i, r in enumerate(results):
            em = r["email"]
            res = r["result"]
            label = res["label"]
            conf = f"{res['confidence']:.0%}"
            sender = em.get("sender_name") or em.get("sender", "")
            if len(sender) > 25:
                sender = sender[:22] + "..."
            subj = em.get("subject", "(Không có tiêu đề)")
            if len(subj) > 35:
                subj = subj[:32] + "..."
            tag = "spam" if label == "Spam" else "normal"
            self.email_tree.insert("", "end", iid=str(i),
                                   values=(sender, subj, em.get("date_str", ""), label, conf),
                                   tags=(tag,))
        self.email_tree.tag_configure("spam", foreground=C["danger"])
        self.email_tree.tag_configure("normal", foreground=C["success"])

    def _on_email_select(self, event):
        sel = self.email_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if idx >= len(self.imap_emails):
            return
        data = self.imap_emails[idx]
        em = data["email"]
        res = data["result"]

        text = f"══ EMAIL CHI TIẾT ══\n\n"
        text += f"Người gửi: {em.get('sender_name', '')} <{em.get('sender', '')}>\n"
        text += f"Ngày: {em.get('date_str', '')}\n"
        text += f"Tiêu đề: {em.get('subject', '')}\n"
        text += f"\n── KẾT QUẢ PHÂN LOẠI ──\n"
        text += f"Nhãn: {res['label']}\n"
        text += f"Độ tin cậy: {res['confidence']:.1%}\n"
        text += f"Phương pháp: {res.get('method', '')}\n"
        if res.get("spam_score"):
            text += f"Spam Score: {res['spam_score']}\n"
        if res.get("details"):
            text += f"\n{res['details']}\n"
        text += f"\n── NỘI DUNG ──\n{em.get('body', '')[:2000]}\n"

        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.config(state="disabled")


if __name__ == "__main__":
    app = EmailClassifierApp()
    app.run()
