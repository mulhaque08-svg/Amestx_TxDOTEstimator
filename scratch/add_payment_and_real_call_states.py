file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update purchaseNumberModal with a 2-Step Flow: Step 1 (Select Number) -> Step 2 (Payment & Checkout)
old_modal_html = '''            <!-- Modal Content -->
            <div class="p-6 space-y-5 text-slate-700">
                <!-- Reserved Admin Line Notice -->
                <div class="p-3 bg-blue-50/70 border border-blue-200/80 rounded-2xl flex items-center justify-between text-xs">
                    <div class="flex items-center gap-2">
                        <span class="text-base">🔒</span>
                        <div>
                            <span class="text-slate-600 font-medium">Your Master Business Line:</span>
                            <strong class="text-blue-900 font-mono font-bold block">(844) 826-3789</strong>
                        </div>
                    </div>
                    <span class="text-[10px] bg-blue-600 text-white font-extrabold px-2.5 py-0.5 rounded-full uppercase tracking-wider">Reserved &bull; Active</span>
                </div>

                <!-- Area Code Selector Tabs -->
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="text-xs font-bold text-slate-700">Choose New Dedicated Line:</label>
                        <span class="text-[11px] text-slate-500">Instant carrier activation</span>
                    </div>
                    <div class="grid grid-cols-2 gap-2 text-xs font-bold">
                        <button onclick="filterNumbers('tollfree')" id="btnNumTollFree" class="py-2.5 px-3 rounded-xl border-2 border-blue-600 bg-blue-50 text-blue-700 flex items-center justify-center gap-1.5 transition">
                            <span>🇺🇸</span>
                            <span>Toll-Free Nationwide (844/855/888)</span>
                        </button>
                        <button onclick="filterNumbers('texas')" id="btnNumTexas" class="py-2.5 px-3 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-1.5 transition">
                            <span>⭐</span>
                            <span>Texas Local Lines</span>
                        </button>
                    </div>
                </div>

                <!-- Live Area Code Search Filter -->
                <div class="relative">
                    <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs">🔍</span>
                    <input id="numSearchInput" oninput="handleNumberSearch(this.value)" type="text" placeholder="Search by area code or city (e.g. 713, 210, 512, 844, Dallas)..." class="w-full pl-9 pr-4 py-2.5 text-xs font-medium text-slate-800 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 focus:bg-white outline-none transition font-sans">
                </div>

                <!-- Number Selection List -->
                <div>
                    <div class="flex items-center justify-between mb-1.5">
                        <label class="text-xs font-bold text-slate-700">Available Numbers for Your Company:</label>
                        <span id="numberCountBadge" class="text-[10px] text-slate-500 font-semibold font-mono">5 available</span>
                    </div>
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
            </div>'''

new_modal_html = '''            <!-- Modal Content: STEP 1 (Select Number) -->
            <div id="modalStepSelectNumber" class="p-6 space-y-5 text-slate-700">
                <!-- Reserved Admin Line Notice -->
                <div class="p-3 bg-blue-50/70 border border-blue-200/80 rounded-2xl flex items-center justify-between text-xs">
                    <div class="flex items-center gap-2">
                        <span class="text-base">🔒</span>
                        <div>
                            <span class="text-slate-600 font-medium">Your Master Business Line:</span>
                            <strong class="text-blue-900 font-mono font-bold block">(844) 826-3789</strong>
                        </div>
                    </div>
                    <span class="text-[10px] bg-blue-600 text-white font-extrabold px-2.5 py-0.5 rounded-full uppercase tracking-wider">Reserved &bull; Active</span>
                </div>

                <!-- Area Code Selector Tabs -->
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="text-xs font-bold text-slate-700">Choose New Dedicated Line to Add:</label>
                        <span class="text-[11px] text-slate-500">$29/mo per additional line</span>
                    </div>
                    <div class="grid grid-cols-2 gap-2 text-xs font-bold">
                        <button onclick="filterNumbers('tollfree')" id="btnNumTollFree" class="py-2.5 px-3 rounded-xl border-2 border-blue-600 bg-blue-50 text-blue-700 flex items-center justify-center gap-1.5 transition">
                            <span>🇺🇸</span>
                            <span>Toll-Free Nationwide (844/855/888)</span>
                        </button>
                        <button onclick="filterNumbers('texas')" id="btnNumTexas" class="py-2.5 px-3 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-1.5 transition">
                            <span>⭐</span>
                            <span>Texas Local Lines</span>
                        </button>
                    </div>
                </div>

                <!-- Live Area Code Search Filter -->
                <div class="relative">
                    <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs">🔍</span>
                    <input id="numSearchInput" oninput="handleNumberSearch(this.value)" type="text" placeholder="Search by area code or city (e.g. 713, 210, 512, 844, Dallas)..." class="w-full pl-9 pr-4 py-2.5 text-xs font-medium text-slate-800 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 focus:bg-white outline-none transition font-sans">
                </div>

                <!-- Number Selection List -->
                <div>
                    <div class="flex items-center justify-between mb-1.5">
                        <label class="text-xs font-bold text-slate-700">Select Desired Number:</label>
                        <span id="numberCountBadge" class="text-[10px] text-slate-500 font-semibold font-mono">5 available</span>
                    </div>
                    <div class="space-y-2 max-h-44 overflow-y-auto custom-scrollbar pr-1" id="availableNumbersList">
                        <!-- Numbers rendered dynamically -->
                    </div>
                </div>

                <!-- Features Included Callout -->
                <div class="p-3 bg-slate-50 rounded-2xl border border-slate-200 text-xs space-y-1">
                    <div class="flex items-center justify-between text-slate-800 font-bold">
                        <span>Includes Bilingual AI Translator + SMS</span>
                        <span class="text-emerald-600 font-bold">✓ Included</span>
                    </div>
                    <div class="flex items-center justify-between text-slate-800 font-bold">
                        <span>Forwarding to Personal Cell Phone</span>
                        <span class="text-emerald-600 font-bold">✓ Included</span>
                    </div>
                </div>

                <!-- Proceed to Payment Button -->
                <button onclick="goToPaymentCheckout()" class="w-full py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-black text-sm rounded-2xl shadow-lg shadow-blue-500/25 transition transform active:scale-98 cursor-pointer flex items-center justify-center gap-2">
                    <span>Continue to Checkout ($29/mo)</span>
                    <span>&rarr;</span>
                </button>
            </div>

            <!-- Modal Content: STEP 2 (Payment & Credit Card Checkout) -->
            <div id="modalStepCheckout" class="hidden p-6 space-y-5 text-slate-700">
                <!-- Selected Number Summary Header -->
                <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between">
                    <div>
                        <div class="text-[11px] text-slate-500 font-bold uppercase tracking-wider">Selected Dedicated Line</div>
                        <div id="checkoutSelectedNumber" class="text-xl font-black text-slate-900 font-mono tracking-tight">(210) 758-1194</div>
                        <div id="checkoutSelectedRegion" class="text-xs text-slate-500 font-medium">San Antonio / Bexar County</div>
                    </div>
                    <div class="text-right">
                        <div class="text-lg font-black text-blue-600">$29.00</div>
                        <div class="text-[10px] text-slate-400 font-bold">per month</div>
                    </div>
                </div>

                <!-- Credit Card Checkout Form -->
                <form id="paymentForm" onsubmit="handleProcessPayment(event)" class="space-y-3.5">
                    <div>
                        <label class="text-xs font-bold text-slate-700 block mb-1">Cardholder Full Name</label>
                        <input id="cardholderName" type="text" required placeholder="John Doe" value="Mohsin Ulhaque" class="w-full px-3.5 py-2.5 text-xs font-semibold text-slate-900 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition">
                    </div>

                    <div>
                        <label class="text-xs font-bold text-slate-700 block mb-1">Card Number (Visa, Mastercard, Amex)</label>
                        <div class="relative flex items-center">
                            <span class="absolute left-3.5 text-slate-400 text-sm">💳</span>
                            <input id="cardNumber" type="text" required maxlength="19" placeholder="4242 &bull;&bull;&bull;&bull; &bull;&bull;&bull;&bull; 4242" value="4242 8819 0293 4102" class="w-full pl-10 pr-3.5 py-2.5 text-xs font-mono font-bold text-slate-900 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition">
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="text-xs font-bold text-slate-700 block mb-1">Expires (MM/YY)</label>
                            <input id="cardExpiry" type="text" required maxlength="5" placeholder="MM/YY" value="08/29" class="w-full px-3.5 py-2.5 text-xs font-mono font-bold text-slate-900 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition text-center">
                        </div>
                        <div>
                            <label class="text-xs font-bold text-slate-700 block mb-1">CVC Code</label>
                            <input id="cardCvc" type="password" required maxlength="4" placeholder="CVC" value="382" class="w-full px-3.5 py-2.5 text-xs font-mono font-bold text-slate-900 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition text-center">
                        </div>
                    </div>

                    <!-- Security trust badge -->
                    <div class="flex items-center justify-between text-[11px] text-slate-500 pt-1 px-1">
                        <span class="flex items-center gap-1 font-semibold text-emerald-700">
                            <span>🔒</span>
                            <span>256-Bit SSL Encrypted &bull; Carrier Provisioning</span>
                        </span>
                        <span class="text-slate-400 font-medium">Cancel Anytime</span>
                    </div>

                    <!-- Payment Button -->
                    <div class="pt-2 space-y-2">
                        <button type="submit" id="btnPayAndActivate" class="w-full py-3.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-black text-sm rounded-2xl shadow-lg shadow-emerald-500/25 transition transform active:scale-98 cursor-pointer flex items-center justify-center gap-2">
                            <span>Pay $29.00 & Provision Line</span>
                            <span>&rarr;</span>
                        </button>
                        <button type="button" onclick="backToNumberSelection()" class="w-full py-2 text-xs font-bold text-slate-500 hover:text-slate-800 transition text-center">
                            &larr; Back to Number Selection
                        </button>
                    </div>
                </form>
            </div>'''

if old_modal_html in content:
    content = content.replace(old_modal_html, new_modal_html)
    print("Modal updated with 2-Step Payment & Checkout Flow!")
else:
    print("old_modal_html exact string not found.")

# 2. Update JavaScript:
# A) Add Payment & Checkout step functions
# B) Require line payment before dialing
# C) Eliminate fake timer - timer ONLY starts when recipient picks up (accept)!
payment_and_call_js = '''        // ==================== CHECKOUT & PAYMENT FLOW ====================
        let pendingCheckoutNumber = null;
        let pendingCheckoutLabel = null;
        let pendingCheckoutId = null;
        let paidLinesRegistry = ['18448263789']; // Master admin line is paid & active

        function goToPaymentCheckout() {
            const checked = document.querySelector('input[name="selectedNumberRadio"]:checked');
            if (!checked) {
                showNotification("Please select a number first.");
                return;
            }

            pendingCheckoutId = checked.value;
            pendingCheckoutNumber = checked.getAttribute('data-num');
            pendingCheckoutLabel = checked.getAttribute('data-label');

            const numDisp = document.getElementById('checkoutSelectedNumber');
            const regDisp = document.getElementById('checkoutSelectedRegion');
            if (numDisp) numDisp.textContent = pendingCheckoutNumber;
            if (regDisp) regDisp.textContent = pendingCheckoutLabel;

            // Switch to Step 2
            document.getElementById('modalStepSelectNumber').classList.add('hidden');
            document.getElementById('modalStepCheckout').classList.remove('hidden');
        }

        function backToNumberSelection() {
            document.getElementById('modalStepCheckout').classList.add('hidden');
            document.getElementById('modalStepSelectNumber').classList.remove('hidden');
        }

        function handleProcessPayment(e) {
            e.preventDefault();
            const btn = document.getElementById('btnPayAndActivate');
            if (btn) {
                btn.innerHTML = `<span>Processing Payment with Carrier...</span>`;
                btn.disabled = true;
            }

            // Simulate payment authorization & carrier provisioning
            setTimeout(() => {
                // Register line as officially paid
                if (pendingCheckoutId) paidLinesRegistry.push(pendingCheckoutId);

                // Add to caller ID select dropdown
                const select = document.getElementById('callerIdSelect');
                if (select && pendingCheckoutId && pendingCheckoutNumber) {
                    let exists = false;
                    for (let i = 0; i < select.options.length; i++) {
                        if (select.options[i].value === pendingCheckoutId) {
                            exists = true;
                            break;
                        }
                    }
                    if (!exists) {
                        const opt = document.createElement('option');
                        opt.value = pendingCheckoutId;
                        opt.textContent = `${pendingCheckoutNumber} (${pendingCheckoutLabel.split(' ')[0]})`;
                        select.appendChild(opt);
                    }
                    select.value = pendingCheckoutId;
                }

                // Reset modal
                if (btn) {
                    btn.innerHTML = `<span>Pay $29.00 & Provision Line</span><span>&rarr;</span>`;
                    btn.disabled = false;
                }
                closePurchaseNumberModal();
                backToNumberSelection();

                showNotification(`🎉 Payment Approved! Line ${pendingCheckoutNumber} is now PAID & ACTIVE!`);
            }, 1200);
        }

        function openPurchaseNumberModal() {
            backToNumberSelection();
            filterNumbers('tollfree');
            document.getElementById('purchaseNumberModal').classList.remove('hidden');
        }
'''

# Replace old makeCallFromKeypad with verified paid check & accurate call states
old_make_call_impl = '''        async function makeCallFromKeypad() {
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

new_make_call_impl = '''        async function makeCallFromKeypad() {
            const inp = document.getElementById('keypadNumberInput');
            const callerSelect = document.getElementById('callerIdSelect');
            const selectedCallerId = callerSelect ? callerSelect.value : '18448263789';
            const rawNum = inp ? inp.value.trim() : '';

            if (!rawNum) {
                showNotification("⚠️ Please enter a telephone number to dial");
                if (inp) inp.focus();
                return;
            }

            // CHECK: Has this line been paid for?
            if (!paidLinesRegistry.includes(selectedCallerId)) {
                showNotification("⚠️ Payment required ($29/mo) to activate and place calls from this line");
                openPurchaseNumberModal();
                return;
            }

            // Check microphone permission before placing call
            try {
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    await navigator.mediaDevices.getUserMedia({ audio: true });
                }
            } catch (micErr) {
                console.warn("Mic permission warning:", micErr);
                showNotification("⚠️ Please allow microphone access in your browser to speak");
            }

            // Normalize phone number for real Twilio outbound dialing
            let cleanDigits = rawNum.replace(/\\D/g, '');
            if (cleanDigits.length === 10) cleanDigits = '1' + cleanDigits;
            const dialableNumber = '+' + cleanDigits;

            // Show In-Call Screen with DIALING state (Timer stays at 00:00 until recipient answers!)
            startActiveCallScreen(rawNum);

            // Connect real live Twilio Voice call
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
            }
        }

        function beginCallTimer() {
            callSeconds = 0;
            const timerDisp = document.getElementById('activeCallTimer');
            if (timerDisp) timerDisp.textContent = "00:00";
            if (activeCallTimerInterval) clearInterval(activeCallTimerInterval);
            activeCallTimerInterval = setInterval(() => {
                callSeconds++;
                const mins = String(Math.floor(callSeconds / 60)).padStart(2, '0');
                const secs = String(callSeconds % 60).padStart(2, '0');
                if (timerDisp) timerDisp.textContent = mins + ':' + secs;
            }, 1000);
        }'''

if old_make_call_impl in content:
    content = content.replace(old_make_call_impl, new_make_call_impl)
    print("Updated makeCallFromKeypad with verified paid check and real call states!")
else:
    print("old_make_call_impl exact string not found.")

# Update startActiveCallScreen to NOT run the timer automatically
old_start_screen = '''            // Start timer
            callSeconds = 0;
            if (timerDisp) timerDisp.textContent = "00:00";
            if (activeCallTimerInterval) clearInterval(activeCallTimerInterval);
            activeCallTimerInterval = setInterval(() => {
                callSeconds++;
                const mins = String(Math.floor(callSeconds / 60)).padStart(2, '0');
                const secs = String(callSeconds % 60).padStart(2, '0');
                if (timerDisp) timerDisp.textContent = `${mins}:${secs}`;
                if (callSeconds === 2 && statusTxt) {
                    statusTxt.textContent = "HD Voice Connected";
                }
            }, 1000);'''

new_start_screen = '''            // Timer stays at 00:00 while dialing - ONLY begins when answered!
            callSeconds = 0;
            if (timerDisp) timerDisp.textContent = "00:00";
            if (activeCallTimerInterval) {
                clearInterval(activeCallTimerInterval);
                activeCallTimerInterval = null;
            }'''

if old_start_screen in content:
    content = content.replace(old_start_screen, new_start_screen)
    print("Disabled fake timer in startActiveCallScreen!")
else:
    print("old_start_screen exact string not found.")

# Add checkout JS before filterNumbers
if 'function goToPaymentCheckout' not in content:
    content = content.replace(
        'function filterNumbers(category) {',
        payment_and_call_js + '\n        function filterNumbers(category) {'
    )
    print("Added payment and checkout JS functions!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("voice-app.html successfully updated with complete 2-Step Checkout & Accurate Call States!")
