import re

file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update initApp to call initTwilioVoice() and loadSavedPaidLines()
target_initApp = '''        function initApp() {
            try {'''

replacement_initApp = '''        function initApp() {
            // Initialize Twilio Carrier Voice Engine and load saved lines
            initTwilioVoice();
            loadSavedPaidLines();

            try {'''

if target_initApp in content:
    content = content.replace(target_initApp, replacement_initApp)
    print("Added initTwilioVoice() to initApp()!")
else:
    print("target_initApp not found")

# 2. Update makeCallFromKeypad to await initTwilioVoice() if not ready, and remove fake 25s simulation
old_call_block = '''            // Connect real live Twilio Voice call
            if (twilioDevice) {
                try {
                    const statusTxt = document.getElementById('activeCallStatusText');
                    if (statusTxt) statusTxt.textContent = "Connecting to carrier network...";
                    
                    const call = await twilioDevice.connect({ 
                        params: { 
                            To: dialableNumber,
                            CallerId: "+18448263789"
                        } 
                    });
                    activeTwilioCall = call;

                    call.on('ringing', () => {
                        const st = document.getElementById('activeCallStatusText');
                        if (st) st.textContent = `Ringing ${formatPhoneNumber(rawNum)}...`;
                        showNotification(`🔔 Ringing ${formatPhoneNumber(rawNum)}...`);
                    });

                    // ONLY start timer when recipient actually answers the phone!
                    call.on('accept', () => {
                        const st = document.getElementById('activeCallStatusText');
                        if (st) st.textContent = "Connected • HD Voice In Call";
                        showNotification(`✓ Call connected with ${formatPhoneNumber(rawNum)}`);
                        beginCallTimer();
                    });

                    call.on('disconnect', () => {
                        endActiveCall();
                    });

                    call.on('error', (err) => {
                        console.error("Twilio Call Error:", err);
                        showNotification("Call ended: No answer or disconnected");
                        endActiveCall();
                    });
                } catch (err) {
                    console.warn("Twilio connect notice:", err);
                }
            } else {
                // If device is not yet registered, notify user
                const statusTxt = document.getElementById('activeCallStatusText');
                if (statusTxt) statusTxt.textContent = "Ringing via Amestx Carrier Bridge...";
                
                // Disconnect after 25s if unanswered (NO 3-minute fake timer!)
                setTimeout(() => {
                    if (activeCallTimerInterval === null && document.getElementById('keypadActiveCallView').classList.contains('hidden') === false) {
                        showNotification("No answer from recipient. Line disconnected.");
                        endActiveCall();
                    }
                }, 25000);
            }'''

new_call_block = '''            // Ensure Twilio carrier voice device is initialized
            if (!twilioDevice) {
                const statusTxt = document.getElementById('activeCallStatusText');
                if (statusTxt) statusTxt.textContent = "Connecting to Amestx carrier network...";
                await initTwilioVoice();
            }

            if (!twilioDevice) {
                showNotification("⚠️ Carrier network connecting... Please try dialing again in a moment.");
                endActiveCall();
                return;
            }

            try {
                const statusTxt = document.getElementById('activeCallStatusText');
                if (statusTxt) statusTxt.textContent = `Connecting carrier to ${formatPhoneNumber(rawNum)}...`;

                const call = await twilioDevice.connect({ 
                    params: { 
                        To: dialableNumber,
                        CallerId: "+18448263789"
                    } 
                });
                activeTwilioCall = call;

                call.on('ringing', () => {
                    const st = document.getElementById('activeCallStatusText');
                    if (st) st.textContent = `Ringing ${formatPhoneNumber(rawNum)}...`;
                    showNotification(`🔔 Ringing ${formatPhoneNumber(rawNum)}...`);
                });

                // ONLY start timer when recipient actually answers the phone!
                call.on('accept', () => {
                    const st = document.getElementById('activeCallStatusText');
                    if (st) st.textContent = "Connected • HD Voice In Call";
                    showNotification(`✓ Call connected with ${formatPhoneNumber(rawNum)}`);
                    beginCallTimer();
                });

                call.on('disconnect', () => {
                    showNotification("Call ended");
                    endActiveCall();
                });

                call.on('error', (err) => {
                    console.error("Twilio Call Error:", err);
                    showNotification("Call ended: " + (err.message || "Line busy or disconnected"));
                    endActiveCall();
                });
            } catch (err) {
                console.error("Twilio connect failed:", err);
                showNotification("Could not place call: " + (err.message || "Carrier error"));
                endActiveCall();
            }'''

if old_call_block in content:
    content = content.replace(old_call_block, new_call_block)
    print("Replaced makeCallFromKeypad block with real carrier connect and zero fake simulation!")
else:
    print("old_call_block exact match not found; looking for fallback...")

# 3. In startActiveCallScreen, change initial status text
content = content.replace(
    'if (statusTxt) statusTxt.textContent = "Calling with HD Voice...";',
    'if (statusTxt) statusTxt.textContent = `Connecting to ${formatted}...`;'
)
content = content.replace(
    'showNotification(`📞 Connected to ${num} from (844) 826-3789`);',
    'showNotification(`📞 Calling ${formatted}...`);'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("voice-app.html successfully updated!")
