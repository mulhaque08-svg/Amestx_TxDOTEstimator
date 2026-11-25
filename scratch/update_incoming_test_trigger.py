file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        function testCallForwardingSimulation() {
            // ZERO POPUPS - In-app live simulation
            showNotification(`🔔 Incoming Call from (512) 472-8819 → Forwarding to your cell ${fwdState.phone}!`);
            
            // Show incoming call banner in the dialer
            const inp = document.getElementById('keypadNumberInput');
            if (inp) inp.value = '+1 (512) 472-8819';
            
            // Trigger in-call state after 1 second
            setTimeout(() => {
                startActiveCallScreen('+1 (512) 472-8819');
            }, 1000);
        }'''

replacement = '''        function testCallForwardingSimulation() {
            handleIncomingTwilioCall({
                parameters: { From: '+1 (832) 390-8863' },
                accept: () => console.log("Twilio WebRTC inbound call accepted!"),
                reject: () => console.log("Twilio WebRTC inbound call rejected!"),
                on: (event, handler) => {}
            });
        }'''

if target in text:
    text = text.replace(target, replacement)
    print("Updated testCallForwardingSimulation to trigger handleIncomingTwilioCall!")
else:
    print("target not found")

# Also check for query param in initApp
init_target = '''        function initApp() {
            // Initialize Twilio Carrier Voice Engine and load saved lines
            initTwilioVoice();
            loadSavedPaidLines();'''

init_replacement = '''        function initApp() {
            // Initialize Twilio Carrier Voice Engine and load saved lines
            initTwilioVoice();
            loadSavedPaidLines();

            // Auto-trigger test incoming call if URL query param is present
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('testIncoming') || urlParams.has('simulateIncoming')) {
                setTimeout(() => testCallForwardingSimulation(), 1200);
            }'''

if init_target in text:
    text = text.replace(init_target, init_replacement)
    print("Added URL query param test trigger to initApp!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("voice-app.html successfully updated for incoming test verification!")
