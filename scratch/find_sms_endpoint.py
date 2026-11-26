with open(r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\backend\whatsapp_translator\main.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('@app.post("/sms"')
if idx == -1:
    idx = text.find("def send_sms")
if idx == -1:
    idx = text.find("/sms")

print("Found index:", idx)
print(text[idx:idx+2500])
