from flask import Flask, render_template, request, send_file
import os
import joblib
import PyPDF2
import docx
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import math
import binascii

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- LOAD AI MODELS ---
print("Loading AI Models...")
try:
    vectorizer = joblib.load('models/vectorizer.pkl')
    classifier = joblib.load('models/classifier.pkl')
except:
    print("WARNING: Models not found. Run train_model.py first!")

# --- HELPER FUNCTIONS ---

def extract_text(filepath):
    ext = filepath.split('.')[-1].lower()
    text = ""
    try:
        if ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        elif ext == 'pdf':
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + " "
        elif ext == 'docx':
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + " "
    except Exception as e:
        return ""
    return text

def internal_nist_check(data_bytes):
    """Basic Monobit Test"""
    bits = ''.join(format(byte, '08b') for byte in data_bytes)
    n = len(bits)
    if n == 0: return "FAIL"
    ones = bits.count('1')
    proportion = ones / n
    if 0.4 < proportion < 0.6:
        return "PASS (Monobit Test)"
    else:
        return "FAIL (Pattern Detected)"

# --- ENCRYPTION ENGINES ---

def encrypt_aes(text):
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(text.encode(), AES.block_size))
    return cipher.iv + ct_bytes, "AES-128 (CBC)"

def encrypt_rsa(text):
    key = RSA.generate(2048)
    public_key = key.publickey()
    cipher = PKCS1_OAEP.new(public_key)
    chunk = text.encode()[:100] 
    ct_bytes = cipher.encrypt(chunk)
    return ct_bytes, "RSA-2048"

def encrypt_hybrid(text):
    aes_key = get_random_bytes(32)
    cipher_aes = AES.new(aes_key, AES.MODE_GCM)
    ciphertext, tag = cipher_aes.encrypt_and_digest(text.encode())
    rsa_key = RSA.generate(2048)
    cipher_rsa = PKCS1_OAEP.new(rsa_key.publickey())
    enc_session_key = cipher_rsa.encrypt(aes_key)
    combined = enc_session_key + cipher_aes.nonce + tag + ciphertext
    return combined, "Hybrid (AES-256 + RSA)"

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files: return "No file"
        file = request.files['file']
        if file.filename == '': return "No file"

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # 1. READ TEXT
        extracted_text = extract_text(filepath)
        if len(extracted_text) < 5:
            return render_template('index.html', error="File is empty or unreadable.")

        # 2. AI ANALYSIS
        tfidf_vector = vectorizer.transform([extracted_text])
        prediction = classifier.predict(tfidf_vector)[0]

        # 3. ENCRYPTION
        if prediction == 'Low':
            raw_cipher_bytes, method = encrypt_aes(extracted_text)
        elif prediction == 'Medium':
            raw_cipher_bytes, method = encrypt_rsa(extracted_text)
        else:
            raw_cipher_bytes, method = encrypt_hybrid(extracted_text)

        # 4. SAVE OUTPUTS
        # Option A: Binary File (for file upload)
        bin_path = os.path.join(UPLOAD_FOLDER, 'cipher_output.bin')
        with open(bin_path, 'wb') as f:
            f.write(raw_cipher_bytes)

        # Option B: Manual Bitstream (0s and 1s string)
        bit_string = ''.join(format(byte, '08b') for byte in raw_cipher_bytes)
        txt_path = os.path.join(UPLOAD_FOLDER, 'manual_bitstream.txt')
        with open(txt_path, 'w') as f:
            f.write(bit_string)

        # 5. INTERNAL CHECK
        nist_status = internal_nist_check(raw_cipher_bytes)
        
        display_cipher = binascii.hexlify(raw_cipher_bytes).decode('utf-8')[:100] + "..."

        return render_template('index.html', 
                               original=extracted_text[:200]+"...", 
                               prediction=prediction,
                               method=method,
                               ciphertext=display_cipher,
                               nist_status=nist_status,
                               show_results=True)

    return render_template('index.html', show_results=False)

@app.route('/download_cipher')
def download_cipher():
    return send_file(os.path.join(UPLOAD_FOLDER, 'cipher_output.bin'), 
                     as_attachment=True, 
                     download_name="ciphertext_file.bin")

@app.route('/download_manual')
def download_manual():
    return send_file(os.path.join(UPLOAD_FOLDER, 'manual_bitstream.txt'), 
                     as_attachment=True, 
                     download_name="manual_bitstream.txt")

if __name__ == '__main__':
    app.run(debug=True)