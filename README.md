🗝️ CryptoLab 2.0 - Multi-language File Encryptor
A simple yet powerful cross-platform desktop application for encrypting and decrypting files using various algorithms. Designed for educational purposes (Lab Work).

✨ Features
Multi-language Support: The interface supports English (EN), Russian (RU), and German (DE). You can switch the language directly from the application menu.
Multiple Algorithms:
AES (Fernet): High-security standard encryption.
XOR: Classic symmetric encryption.
Caesar (Shift): Byte-shifting algorithm.
Reverse: Simple byte inversion.
Safe Output: Decrypted files are automatically saved with an _uncrptd suffix to prevent overwriting original files.
Modern UI: Dark-themed interface with intuitive controls.
🛠️ Installation
Clone this repository.
Install the required cryptography library:
pip install cryptography
Run the application:
bash

python main.py
📖 Usage
Select Language: Use the dropdown at the top right to choose your preferred language (EN/RU/DE).
Choose a Tab: Select "Encryption" or "Decryption".
Select Algorithm: Choose the encryption method from the list.
Select File: Click the folder icon to choose a .txt or .docx file.
Enter Password: Type your secret keyword (supports Cyrillic and Latin characters).
Execute: Click the action button. The result will be saved in the same folder as the source file.
📂 Project Structure
main.py - Main application source code.
README.md - This file.
.gitignore - Git ignore rules.