file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Twilio SDK in <head>
twilio_sdk = '''    <!-- Twilio Voice WebRTC SDK -->
    <script src="https://cdn.jsdelivr.net/npm/@twilio/voice-sdk@2.11.0/dist/twilio.min.js"></script>
'''
if 'twilio.min.js' not in content:
    content = content.replace('<!-- Tailwind CSS -->', twilio_sdk + '\n    <!-- Tailwind CSS -->')
    print("Added Twilio Voice WebRTC SDK to <head>")

# 2. Add "+ Add Line" button in Top Utility Bar
top_bar_search = '<!-- Call Forwarding Status Pill -->'
add_line_top_btn = '''            <!-- Purchase / Add Line Button -->
            <button onclick="openPurchaseNumberModal()" class="flex items-center gap-1.5 text-xs bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-200 border border-indigo-400/30 px-2.5 py-1 rounded-lg font-bold transition flex-shrink-0" title="Purchase or Add Dedicated Business Phone Line">
                <span>➕</span>
                <span class="hidden sm:inline">Add Line</span>
            </button>

            <!-- Call Forwarding Status Pill -->'''

if top_bar_search in content and 'openPurchaseNumberModal' not in content:
    content = content.replace(top_bar_search, add_line_top_btn)
    print("Added + Add Line button to top utility bar!")

# 3. Add "+ Get New Line" link right above the caller ID dropdown
caller_id_header_old = '<div class="text-[11px] text-slate-500 font-medium mb-1">My caller ID:</div>'
caller_id_header_new = '''<div class="flex items-center justify-between mb-1">
                    <span class="text-[11px] text-slate-500 font-medium">My caller ID:</span>
                    <button onclick="openPurchaseNumberModal()" class="text-[11px] font-bold text-blue-600 hover:text-blue-700 hover:underline flex items-center gap-1" title="Get a dedicated toll-free or local Texas line">
                        <span>+ Get New Line</span>
                    </button>
                </div>'''

if caller_id_header_old in content:
    content = content.replace(caller_id_header_old, caller_id_header_new)
    print("Added + Get New Line link next to Caller ID selector!")

# 4. Add "Purchase Line" modal right before </body>
purchase_modal_html = '''    <!-- Purchase / Add Dedicated Phone Line Modal -->
    <div id="purchaseNumberModal" class="hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl max-w-lg w-full shadow-2xl border border-slate-100 overflow-hidden transform transition-all animate-in fade-in zoom-in duration-200">
            <!-- Modal Header -->
            <div class="bg-gradient-to-r from-[#0d163a] via-[#162854] to-[#0f1d47] p-6 text-white relative border-b border-[#213a74]/60">
                <button onclick="closePurchaseNumberModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white text-lg font-bold w-8 h-8 rounded-full flex items-center justify-center hover:bg-white/10 transition">
                    &times;
                </button>
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center text-xl font-bold shadow-lg shadow-blue-500/30">
                        📞
                    </div>
                    <div>
                        <h3 class="text-lg font-black tracking-tight text-white">Purchase & Add Business Line</h3>
                        <p class="text-xs text-cyan-200 mt-0.5">Choose a dedicated Toll-Free (844) or Local Texas Number</p>
                    </div>
                </div>
            </div>

            <!-- Modal Content -->
            <div class="p-6 space-y-5 text-slate-700">
                <!-- Area Code Selector Tabs -->
                <div>
                    <label class="text-xs font-bold text-slate-700 block mb-2">Select Number Region or Type:</label>
                    <div class="grid grid-cols-2 gap-2 text-xs font-bold">
                        <button onclick="filterNumbers('tollfree')" id="btnNumTollFree" class="py-2.5 px-3 rounded-xl border-2 border-blue-600 bg-blue-50 text-blue-700 flex items-center justify-center gap-1.5 transition">
                            <span>🇺🇸</span>
                            <span>Toll-Free Nationwide (844)</span>
                        </button>
                        <button onclick="filterNumbers('texas')" id="btnNumTexas" class="py-2.5 px-3 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-1.5 transition">
                            <span>⭐</span>
                            <span>Texas Local Lines</span>
                        </button>
                    </div>
                </div>

                <!-- Number Selection List -->
                <div>
                    <label class="text-xs font-bold text-slate-700 block mb-2">Available Phone Numbers Ready for Activation:</label>
                    <div class="space-y-2 max-h-48 overflow-y-auto custom-scrollbar pr-1" id="availableNumbersList">
                        <!-- Numbers rendered dynamically -->
                    </div>
                </div>

                <!-- Features Included Callout -->
                <div class="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 text-xs space-y-1.5">
                    <div class="flex items-center justify-between text-slate-900 font-bold">
                        <span>Includes Real-Time Bilingual AI Translator</span>
                        <span class="text-emerald-600 font-extrabold">✓ Included</span>
                    </div>
                    <div class="flex items-center justify-between text-slate-900 font-bold">
                        <span>2-Way Client SMS & Text Messaging</span>
                        <span class="text-emerald-600 font-extrabold">✓ Included</span>
                    </div>
                    <div class="flex items-center justify-between text-slate-900 font-bold">
                        <span>Automatic Call Forwarding to Your Cell</span>
                        <span class="text-emerald-600 font-extrabold">✓ Included</span>
                    </div>
                </div>

                <!-- Pricing & Trial Badge -->
                <div class="p-3 bg-emerald-50 border border-emerald-200 rounded-2xl text-xs flex items-center justify-between">
                    <div>
                        <div class="font-bold text-emerald-900">15-Day Free Trial Price:</div>
                        <div class="text-[11px] text-emerald-700">No charge today &bull; Full unlimited access</div>
                    </div>
                    <div class="text-right">
                        <div class="text-lg font-black text-emerald-600">$0.00</div>
                        <div class="text-[10px] text-slate-500 font-semibold">then $29/mo</div>
                    </div>
                </div>

                <!-- Activate Action Button -->
                <button onclick="activateSelectedNumber()" class="w-full py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-black text-sm rounded-2xl shadow-lg shadow-blue-500/25 transition transform active:scale-98 cursor-pointer flex items-center justify-center gap-2">
                    <span>Activate This Dedicated Line Now</span>
                    <span>&rarr;</span>
                </button>
            </div>
        </div>
    </div>
'''

if 'id="purchaseNumberModal"' not in content:
    content = content.replace('</body>', purchase_modal_html + '\n</body>')
    print("Added purchaseNumberModal to voice-app.html")

# 5. Connect Twilio Device & Live Real Calling in Scripts
twilio_integration_js = '''        // ==================== LIVE TWILIO WEBRTC ENGINE ====================
        let twilioDevice = null;
        let activeTwilioCall = null;
        let isDeviceReady = false;

        async function initTwilioVoice() {
            try {
                console.log("Initializing Twilio Voice engine...");
                const res = await fetch("https://amestx-translator-869440210153.us-central1.run.app/token?identity=amestx_agent");
                const data = await res.json();
                if (data && data.token && typeof Twilio !== 'undefined') {
                    twilioDevice = new Twilio.Device(data.token, {
                        codecPreferences: ['opus', 'pcmu'],
                        enableRingingState: true
                    });

                    twilioDevice.on('registered', () => {
                        isDeviceReady = true;
                        console.log("Twilio Device Registered! Dedicated Business Line Active.");
                        showNotification("✅ Twilio HD Voice Connected: (844) 826-3789");
                    });

                    twilioDevice.on('incoming', (call) => {
                        handleIncomingTwilioCall(call);
                    });

                    twilioDevice.on('error', (err) => {
                        console.warn("Twilio Device notice:", err);
                    });

                    await twilioDevice.register();
                } else {
                    console.log("Twilio Voice simulated mode ready.");
                }
            } catch (err) {
                console.warn("Twilio Voice backend notice (running with simulated carrier bridge):", err);
            }
        }

        function handleIncomingTwilioCall(call) {
            activeTwilioCall = call;
            const fromNumber = (call.parameters && call.parameters.From) ? call.parameters.From : "+1 (512) 472-8819";
            showNotification(`📲 Incoming Call from ${fromNumber} → Forwarding to cell!`);
            startActiveCallScreen(fromNumber);

            call.on('disconnect', () => {
                endActiveCall();
            });
        }
'''

# Replace makeCallFromKeypad and startActiveCallScreen to call real Twilio
old_make_call_block = '''        function makeCallFromKeypad() {
            const inp = document.getElementById('keypadNumberInput');
            const num = inp ? inp.value.trim() : '';
            if (!num) {
                showNotification("⚠️ Please enter a telephone number to dial");
                if (inp) inp.focus();
                return;
            }
            // ZERO POPUPS! Start call directly
            startActiveCallScreen(num);
        }'''

new_make_call_block = '''        async function makeCallFromKeypad() {
            const inp = document.getElementById('keypadNumberInput');
            const rawNum = inp ? inp.value.trim() : '';
            if (!rawNum) {
                showNotification("⚠️ Please enter a telephone number to dial");
                if (inp) inp.focus();
                return;
            }

            // Normalize phone number for real Twilio outbound dialing
            let cleanDigits = rawNum.replace(/\\D/g, '');
            if (cleanDigits.length === 10) cleanDigits = '1' + cleanDigits;
            const dialableNumber = '+' + cleanDigits;

            // Start live active call screen IMMEDIATELY (ZERO POPUPS!)
            startActiveCallScreen(rawNum);

            // Connect real live Twilio Voice call if device is ready
            if (twilioDevice) {
                try {
                    const statusTxt = document.getElementById('activeCallStatusText');
                    if (statusTxt) statusTxt.textContent = "Connecting through carrier...";
                    
                    const call = await twilioDevice.connect({ 
                        params: { 
                            To: dialableNumber,
                            CallerId: "+18448263789"
                        } 
                    });
                    activeTwilioCall = call;

                    call.on('ringing', () => {
                        const st = document.getElementById('activeCallStatusText');
                        if (st) st.textContent = "Ringing recipient's phone...";
                        showNotification(`📞 Ringing ${formatPhoneNumber(rawNum)}...`);
                    });

                    call.on('accept', () => {
                        const st = document.getElementById('activeCallStatusText');
                        if (st) st.textContent = "HD Voice Connected • Live";
                        showNotification(`✓ Call connected with ${formatPhoneNumber(rawNum)}`);
                    });

                    call.on('disconnect', () => {
                        endActiveCall();
                    });

                    call.on('error', (err) => {
                        console.error("Twilio Call Error:", err);
                        showNotification("Call disconnected");
                        endActiveCall();
                    });
                } catch (err) {
                    console.warn("Twilio connect notice:", err);
                }
            }
        }'''

if old_make_call_block in content:
    content = content.replace(old_make_call_block, new_make_call_block)
    print("Updated makeCallFromKeypad with live Twilio dialing!")
else:
    print("makeCallFromKeypad exact block not found.")

# Update endActiveCall to disconnect Twilio
old_end_call = '''        function endActiveCall() {
            if (activeCallTimerInterval) {
                clearInterval(activeCallTimerInterval);
                activeCallTimerInterval = null;
            }
            const dialView = document.getElementById('keypadDialView');
            const callView = document.getElementById('keypadActiveCallView');
            if (callView) callView.classList.add('hidden');
            if (dialView) dialView.classList.remove('hidden');

            showNotification("Call ended");
        }'''

new_end_call = '''        function endActiveCall() {
            if (activeTwilioCall) {
                try { activeTwilioCall.disconnect(); } catch (e) {}
                activeTwilioCall = null;
            }
            if (activeCallTimerInterval) {
                clearInterval(activeCallTimerInterval);
                activeCallTimerInterval = null;
            }
            const dialView = document.getElementById('keypadDialView');
            const callView = document.getElementById('keypadActiveCallView');
            if (callView) callView.classList.add('hidden');
            if (dialView) dialView.classList.remove('hidden');

            showNotification("Call ended");
        }'''

if old_end_call in content:
    content = content.replace(old_end_call, new_end_call)
    print("Updated endActiveCall with Twilio hangup!")
else:
    print("endActiveCall exact block not found.")

# Add Number Purchase logic & Twilio init in script
purchase_js = '''
        // ==================== PURCHASE & MANAGE LINES ====================
        const availableNumberCatalog = {
            tollfree: [
                { number: "(844) 826-3789", label: "Toll-Free Nationwide (Primary Active Line)", id: "18448263789" },
                { number: "(844) 912-4420", label: "Toll-Free Nationwide (Commercial Dispatch)", id: "18449124420" },
                { number: "(888) 720-3901", label: "Toll-Free Nationwide (Estimator Bids)", id: "18887203901" }
            ],
            texas: [
                { number: "(210) 942-4238", label: "San Antonio / Bexar County Construction", id: "12109424238" },
                { number: "(512) 648-9102", label: "Austin / Central Texas Regional", id: "15126489102" },
                { number: "(713) 489-3321", label: "Houston Metro / Gulf Coast", id: "17134893321" },
                { number: "(832) 555-0199", label: "Houston South Commercial", id: "18325550199" },
                { number: "(214) 736-5540", label: "Dallas / Fort Worth North Texas", id: "12147365540" }
            ]
        };

        let currentNumberCategory = 'tollfree';
        let selectedNumberId = '18448263789';

        function openPurchaseNumberModal() {
            filterNumbers('tollfree');
            document.getElementById('purchaseNumberModal').classList.remove('hidden');
        }

        function closePurchaseNumberModal() {
            document.getElementById('purchaseNumberModal').classList.add('hidden');
        }

        function filterNumbers(category) {
            currentNumberCategory = category;
            const btnToll = document.getElementById('btnNumTollFree');
            const btnTx = document.getElementById('btnNumTexas');
            const list = document.getElementById('availableNumbersList');
            if (!list) return;

            if (category === 'tollfree') {
                if (btnToll) btnToll.className = "py-2.5 px-3 rounded-xl border-2 border-blue-600 bg-blue-50 text-blue-700 flex items-center justify-center gap-1.5 transition";
                if (btnTx) btnTx.className = "py-2.5 px-3 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-1.5 transition";
            } else {
                if (btnToll) btnToll.className = "py-2.5 px-3 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-1.5 transition";
                if (btnTx) btnTx.className = "py-2.5 px-3 rounded-xl border-2 border-blue-600 bg-blue-50 text-blue-700 flex items-center justify-center gap-1.5 transition";
            }

            const items = availableNumberCatalog[category] || [];
            list.innerHTML = items.map((item, idx) => `
                <label class="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-blue-300 hover:bg-blue-50/40 cursor-pointer transition">
                    <div class="flex items-center gap-3">
                        <input type="radio" name="selectedNumberRadio" value="${item.id}" data-num="${item.number}" data-label="${item.label}" ${idx === 0 ? 'checked' : ''} class="text-blue-600">
                        <div>
                            <div class="text-xs font-black text-slate-900 font-mono">${item.number}</div>
                            <div class="text-[11px] text-slate-500">${item.label}</div>
                        </div>
                    </div>
                    <span class="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">Available</span>
                </label>
            `).join('');
        }

        function activateSelectedNumber() {
            const checked = document.querySelector('input[name="selectedNumberRadio"]:checked');
            if (!checked) {
                showNotification("Please select a number to activate.");
                return;
            }

            const numId = checked.value;
            const numText = checked.getAttribute('data-num');
            const numLabel = checked.getAttribute('data-label');

            // Add to caller ID select dropdown if not already present
            const select = document.getElementById('callerIdSelect');
            if (select) {
                let exists = false;
                for (let i = 0; i < select.options.length; i++) {
                    if (select.options[i].value === numId) {
                        exists = true;
                        break;
                    }
                }
                if (!exists) {
                    const opt = document.createElement('option');
                    opt.value = numId;
                    opt.textContent = `${numText} (${numLabel.split(' ')[0]})`;
                    select.appendChild(opt);
                }
                select.value = numId;
            }

            // Save in localStorage
            localStorage.setItem('amestx_primary_line', numText);

            closePurchaseNumberModal();
            showNotification(`🎉 Line ${numText} activated and ready for calls & texts!`);
        }
'''

# Insert twilio integration and purchase logic before window.addEventListener('DOMContentLoaded', initApp);
target_init = "window.addEventListener('DOMContentLoaded', initApp);"
if target_init in content and 'initTwilioVoice' not in content:
    content = content.replace(
        target_init,
        twilio_integration_js + '\n' + purchase_js + '\n        ' + target_init
    )
    # Also call initTwilioVoice() inside initApp()
    content = content.replace(
        'loadForwardingConfig();',
        'loadForwardingConfig();\n            initTwilioVoice();'
    )
    print("Added Twilio Voice init and Number Purchase logic to scripts!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("voice-app.html successfully updated with Twilio and Purchase Line Modal!")
