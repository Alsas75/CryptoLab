import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from cryptography.fernet import Fernet, InvalidToken
import base64
import hashlib

# --- СПИСОК ПЕРЕВОДОВ (I18N) ---
LANGUAGES = {
    "ru": {
        "app_title": "CryptoLab 2.0",
        "tab_encrypt": " 🔒 ШИФРОВАНИЕ ",
        "tab_decrypt": " 🔓 ДЕШИФРОВКА ",
        "lbl_algo": "Метод шифрования:",
        "lbl_file": "Выберите файл:",
        "lbl_pass": "Кодовое слово:",
        "btn_encrypt": " 🔐 ЗАШИФРОВАТЬ ФАЙЛ",
        "btn_decrypt": " 🔓 РАСШИФРОВАТЬ ФАЙЛ",
        "status_ready": "Готов к работе",
        "status_processing": "Обработка файла...",
        "status_done": "Готово!",
        "err_no_file": "Файл не выбран или не существует!",
        "err_no_pass": "Введите кодовое слово!",
        "err_wrong_pass": "Неверный пароль или данные повреждены!",
        "msg_success_title": "Успех",
        "msg_success_text": "Операция '{op}' завершена.\nФайл сохранен как:\n{name}",
        "lang_label": "Язык / Language / Sprache:",
        "algo_aes": "AES (Fernet) - Стандарт",
        "algo_xor": "XOR - Симметричный",
        "algo_caesar": "Caesar (Shift) - Сдвиг",
        "algo_reverse": "Reverse - Инверсия"
    },
    "en": {
        "app_title": "CryptoLab 2.0",
        "tab_encrypt": " 🔒 ENCRYPTION ",
        "tab_decrypt": " 🔓 DECRYPTION ",
        "lbl_algo": "Encryption Method:",
        "lbl_file": "Select File:",
        "lbl_pass": "Password:",
        "btn_encrypt": " 🔐 ENCRYPT FILE",
        "btn_decrypt": " 🔓 DECRYPT FILE",
        "status_ready": "Ready to work",
        "status_processing": "Processing file...",
        "status_done": "Done!",
        "err_no_file": "File not selected or does not exist!",
        "err_no_pass": "Please enter a password!",
        "err_wrong_pass": "Wrong password or data corrupted!",
        "msg_success_title": "Success",
        "msg_success_text": "Operation '{op}' completed.\nFile saved as:\n{name}",
        "lang_label": "Language:",
        "algo_aes": "AES (Fernet) - Standard",
        "algo_xor": "XOR - Symmetric",
        "algo_caesar": "Caesar (Shift)",
        "algo_reverse": "Reverse - Inversion"
    },
    "de": {
        "app_title": "CryptoLab 2.0",
        "tab_encrypt": " 🔒 VERSCHLÜSSELUNG ",
        "tab_decrypt": " 🔓 ENTSCHLÜSSELUNG ",
        "lbl_algo": "Verschlüsselungsmethode:",
        "lbl_file": "Datei auswählen:",
        "lbl_pass": "Passwort:",
        "btn_encrypt": " 🔐 DATEI VERSCHLÜSSELN",
        "btn_decrypt": " 🔓 DATEI ENTSCHLÜSSELN",
        "status_ready": "Bereit zur Arbeit",
        "status_processing": "Datei wird verarbeitet...",
        "status_done": "Fertig!",
        "err_no_file": "Datei nicht ausgewählt oder existiert nicht!",
        "err_no_pass": "Bitte Passwort eingeben!",
        "err_wrong_pass": "Falsches Passwort oder Daten beschädigt!",
        "msg_success_title": "Erfolg",
        "msg_success_text": "Vorgang '{op}' abgeschlossen.\nDatei gespeichert als:\n{name}",
        "lang_label": "Sprache:",
        "algo_aes": "AES (Fernet) - Standard",
        "algo_xor": "XOR - Symmetrisch",
        "algo_caesar": "Caesar (Verschiebung)",
        "algo_reverse": "Reverse - Umkehrung"
    }
}


# --- КОНФИГУРАЦИЯ СТИЛЕЙ ---
class Styles:
    BG_COLOR = "#2b2b2b"
    FG_COLOR = "#ffffff"
    ACCENT_COLOR = "#3c3f41"
    BTN_COLOR = "#4a90e2"
    BTN_TEXT = "#ffffff"
    ENTRY_BG = "#ffffff"
    ENTRY_FG = "#000000"
    FONT = ("Segoe UI", 10)
    HEADER_FONT = ("Segoe UI", 11, "bold")


class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = "en"  # Язык по умолчанию

        # Настройка корня
        self.root.configure(bg=Styles.BG_COLOR)
        self.setup_styles()

        # Верхняя панель управления (Выбор языка)
        self.top_bar = tk.Frame(self.root, bg=Styles.BG_COLOR, pady=10)
        self.top_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(self.top_bar, text=self.t("lang_label"), bg=Styles.BG_COLOR, fg=Styles.FG_COLOR,
                 font=Styles.FONT).pack(side=tk.LEFT, padx=20)

        self.lang_combo = ttk.Combobox(self.top_bar, values=["English", "Русский", "Deutsch"], state="readonly",
                                       width=15)
        self.lang_combo.current(0)  # Индекс 0 = English
        self.lang_combo.bind("<<ComboboxSelected>>", self.change_language)
        self.lang_combo.pack(side=tk.LEFT, padx=10)

        # Основная область (Пересоздается при смене языка)
        self.main_container = tk.Frame(self.root, bg=Styles.BG_COLOR)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Первый запуск UI
        self.build_ui()

        # Статус бар
        self.status_var = tk.StringVar(value=self.t("status_ready"))
        status_lbl = tk.Label(self.root, textvariable=self.status_var,
                              bg=Styles.BG_COLOR, fg=Styles.FG_COLOR, font=("Segoe UI", 9), anchor="w")
        status_lbl.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 10))

    def t(self, key):
        """Вспомогательный метод для получения текста на текущем языке"""
        return LANGUAGES[self.current_lang].get(key, key)

    def change_language(self, event):
        """Обработчик смены языка"""
        selected = self.lang_combo.get()
        if selected == "English":
            self.current_lang = "en"
        elif selected == "Русский":
            self.current_lang = "ru"
        elif selected == "Deutsch":
            self.current_lang = "de"

        # Перерисовываем заголовок окна и UI
        self.root.title(self.t("app_title"))
        self.main_container.destroy()
        self.main_container = tk.Frame(self.root, bg=Styles.BG_COLOR)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.build_ui()
        self.status_var.set(self.t("status_ready"))

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=Styles.BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", padding=[15, 10], background=Styles.ACCENT_COLOR,
                        foreground=Styles.FG_COLOR, borderwidth=0, font=Styles.FONT)
        style.map("TNotebook.Tab", background=[("selected", Styles.BTN_COLOR)])
        style.configure("Dark.TCombobox", fieldbackground=Styles.ENTRY_BG, background=Styles.ENTRY_BG,
                        foreground=Styles.ENTRY_FG)

    def build_ui(self):
        """Построение интерфейса на основе текущего языка"""
        inner_frame = tk.Frame(self.main_container, bg=Styles.BG_COLOR, padx=20, pady=10)
        inner_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook (Вкладки)
        self.notebook = ttk.Notebook(inner_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка 1
        self.tab_encrypt = tk.Frame(self.notebook, bg=Styles.ACCENT_COLOR)
        self.notebook.add(self.tab_encrypt, text=self.t("tab_encrypt"))
        self.create_tab_content(self.tab_encrypt, "encrypt")

        # Вкладка 2
        self.tab_decrypt = tk.Frame(self.notebook, bg=Styles.ACCENT_COLOR)
        self.notebook.add(self.tab_decrypt, text=self.t("tab_decrypt"))
        self.create_tab_content(self.tab_decrypt, "decrypt")

    def create_tab_content(self, parent, mode):
        card = tk.Frame(parent, bg=Styles.ACCENT_COLOR, padx=25, pady=25)
        card.pack(fill=tk.BOTH, expand=True)

        # Алгоритм
        tk.Label(card, text=self.t("lbl_algo"), bg=Styles.ACCENT_COLOR, fg=Styles.FG_COLOR,
                 font=Styles.HEADER_FONT).grid(row=0, column=0, sticky="w", pady=(0, 5))
        algo_list = [self.t("algo_aes"), self.t("algo_xor"), self.t("algo_caesar"), self.t("algo_reverse")]
        self.algo_combo = ttk.Combobox(card, values=algo_list, state="readonly", font=Styles.FONT, width=35,
                                       style="Dark.TCombobox")
        self.algo_combo.current(0)
        self.algo_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # Файл
        tk.Label(card, text=self.t("lbl_file"), bg=Styles.ACCENT_COLOR, fg=Styles.FG_COLOR,
                 font=Styles.HEADER_FONT).grid(row=2, column=0, sticky="w", pady=(0, 5))
        file_frame = tk.Frame(card, bg=Styles.ACCENT_COLOR)
        file_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        self.path_entry = tk.Entry(file_frame, font=("Segoe UI", 9), bg=Styles.ENTRY_BG, fg=Styles.ENTRY_FG, bd=0,
                                   relief="flat")
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=5)

        tk.Button(file_frame, text=" 📂 ", bg="#555", fg="white", bd=0, relief="flat",
                  command=lambda: self.select_file()).pack(side="left", padx=(10, 0), ipady=5, ipadx=10)

        # Пароль
        tk.Label(card, text=self.t("lbl_pass"), bg=Styles.ACCENT_COLOR, fg=Styles.FG_COLOR,
                 font=Styles.HEADER_FONT).grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.pass_entry = tk.Entry(card, show="•", font=("Segoe UI", 9), bg=Styles.ENTRY_BG, fg=Styles.ENTRY_FG, bd=0,
                                   relief="flat")
        self.pass_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 25), ipady=5)

        # Кнопка
        btn_text = self.t("btn_encrypt") if mode == "encrypt" else self.t("btn_decrypt")
        tk.Button(card, text=btn_text, bg=Styles.BTN_COLOR, fg="white", font=("Segoe UI", 11, "bold"),
                  relief="flat", cursor="hand2",
                  command=lambda: self.process_file(mode)).grid(row=6, column=0, columnspan=2, sticky="ew", ipady=10)

        card.columnconfigure(0, weight=1)

    def select_file(self):
        filename = filedialog.askopenfilename(title="Select File",
                                              filetypes=[("Documents", "*.txt *.docx"), ("All", "*.*")])
        if filename:
            self.path_entry.delete(0, tk.END)
            if len(filename) > 50:
                self.path_entry.insert(0, "..." + filename[-47:])
            else:
                self.path_entry.insert(0, filename)
            self.path_entry.xview_moveto(1)

    # --- ЛОГИКА ШИФРОВАНИЯ (Без изменений) ---
    def get_fernet_key(self, password):
        return base64.urlsafe_b64encode(hashlib.sha256(password.encode('utf-8')).digest())

    def crypt_xor(self, data, password):
        k = password.encode('utf-8')
        return bytes([a ^ b for a, b in zip(data, (k * (len(data) // len(k) + 1))[:len(data)])])

    def crypt_caesar(self, data, password):
        s = sum(password.encode('utf-8')) % 256
        return bytes([(b + s) % 256 for b in data])

    def crypt_reverse(self, data, password):
        return data[::-1]

    def process_file(self, mode):
        filepath = self.path_entry.get()
        password = self.pass_entry.get()
        algo_name = self.algo_combo.get()

        # Валидация
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", self.t("err_no_file"))
            return
        if not password:
            messagebox.showerror("Error", self.t("err_no_pass"))
            return

        try:
            self.status_var.set(self.t("status_processing"))
            self.root.update()

            with open(filepath, "rb") as f:
                data = f.read()
            algo = algo_name.split()[0]
            result = None

            if algo == "AES" or algo == "AES" in algo_name:  # Обработка разных языков в названии
                key = self.get_fernet_key(password)
                f = Fernet(key)
                result = f.encrypt(data) if mode == "encrypt" else f.decrypt(data)
            elif algo == "XOR":
                result = self.crypt_xor(data, password)
            elif algo == "Caesar":
                result = self.crypt_caesar(data, password)
            elif algo == "Reverse":
                result = self.crypt_reverse(data, password)

            # Имена файлов
            base = os.path.dirname(filepath)
            name = os.path.basename(filepath)

            if mode == "encrypt":
                out_name = name + ".enc"
            else:
                clean = name[:-4] if name.endswith(".enc") else name
                n, ext = os.path.splitext(clean)
                out_name = f"{n}_uncrptd{ext}"

            out_path = os.path.join(base, out_name)
            with open(out_path, "wb") as f:
                f.write(result)

            self.status_var.set(self.t("status_done"))
            messagebox.showinfo(self.t("msg_success_title"),
                                self.t("msg_success_text").format(op=mode, name=out_name))

        except InvalidToken:
            self.status_var.set("Error")
            messagebox.showerror("Error", self.t("err_wrong_pass"))
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()