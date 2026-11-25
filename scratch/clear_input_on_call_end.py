file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update endActiveCall to clear keypadNumberInput
old_end_active_call = '''            if (callView) callView.classList.add('hidden');
            if (dialView) dialView.classList.remove('hidden');

            showNotification("Call ended");'''

new_end_active_call = '''            if (callView) callView.classList.add('hidden');
            if (dialView) dialView.classList.remove('hidden');

            // Reset dialed number to blank for the next new call
            const kpInput = document.getElementById('keypadNumberInput');
            if (kpInput) {
                kpInput.value = '';
            }

            showNotification("Call ended");'''

if old_end_active_call in text:
    text = text.replace(old_end_active_call, new_end_active_call)
    print("Added input clear to endActiveCall!")
else:
    print("old_end_active_call not found")

# 2. Update hideIncomingCallUI to clear keypadNumberInput
old_hide_incoming = '''            if (ringingControls) ringingControls.classList.add('hidden');
            if (connectedControls) connectedControls.classList.remove('hidden');
        }'''

new_hide_incoming = '''            if (ringingControls) ringingControls.classList.add('hidden');
            if (connectedControls) connectedControls.classList.remove('hidden');

            // Reset dialed number to blank
            const kpInput = document.getElementById('keypadNumberInput');
            if (kpInput) {
                kpInput.value = '';
            }
        }'''

if old_hide_incoming in text:
    text = text.replace(old_hide_incoming, new_hide_incoming)
    print("Added input clear to hideIncomingCallUI!")
else:
    print("old_hide_incoming not found")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("voice-app.html successfully updated to clear dialed numbers on call end!")
