file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace Left Sidebar alert buttons with real actions & non-blocking toasts
sidebar_replacements = [
    (
        'onclick="alert(\'Message: Internal team chat and direct messaging.\')"',
        'onclick="switchToTextMessenger(); showNotification(\'💬 Team & Client Messaging Connected\');"'
    ),
    (
        'onclick="alert(\'Video: 1-click video meeting bridge.\')"',
        'onclick="showNotification(\'📹 1-Click Video Bridge: Ready\');"'
    ),
    (
        'onclick="alert(\'AIR: Amestx Bilingual AI Assistant (Spanish & English translation).\')"',
        'onclick="toggleAirAiAssistant();"'
    ),
    (
        'onclick="alert(\'Text: 2-way client SMS with instant Spanish translation.\')"',
        'onclick="switchToTextMessenger();"'
    ),
    (
        'onclick="alert(\'Fax: Cloud digital faxing for construction bids & TxDOT plans.\')"',
        'onclick="showNotification(\'📠 Cloud Digital Fax: Ready for PDF uploads\');"'
    ),
    (
        'onclick="alert(\'Webinar: Live team broadcasts and subcontractor bid conferences.\')"',
        'onclick="showNotification(\'📡 Broadcast Webinar Bridge: Ready\');"'
    ),
    (
        'onclick="alert(\'Amestx Priority Support: 1-844-826-3789\')"',
        'onclick="showNotification(\'📞 Amestx Priority Support: 1-844-826-3789 (Toll-Free)\');"'
    ),
    (
        'onclick="alert(\'Help: Inbound calls to (844) 826-3789 can be answered in this web dialer or forwarded automatically to your personal cell phone.\')"',
        'onclick="showNotification(\'ℹ️ Inbound calls can be answered here or forwarded to cell.\');"'
    )
]

for old, new in sidebar_replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"Replaced sidebar alert: {old[:30]}...")
    else:
        print(f"Sidebar string not found: {old[:30]}...")

# 2. Add in-call screen to Column 2 (Phone Dialpad)
old_dialer_body = '''            <!-- Enter a name or number Input -->
            <div class="px-5 pt-2 pb-1">
                <div class="relative flex items-center">
                    <input id="keypadNumberInput" type="tel" placeholder="Enter a name or number" class="w-full bg-transparent border-b border-slate-200 focus:border-blue-600 py-2 pr-8 text-sm font-semibold text-slate-800 placeholder-slate-400 outline-none transition font-sans">
                    <button onclick="clearKeypadDigit()" class="absolute right-0 text-slate-400 hover:text-slate-700 p-1 text-sm transition" title="Clear">
                        ⌫
                    </button>
                </div>
            </div>

            <!-- Numeric Keypad (RingCentral Minimalist Style) -->
            <div class="px-6 py-2 flex-1 flex flex-col justify-center">
                <div class="grid grid-cols-3 gap-y-3 gap-x-4 max-w-[220px] mx-auto w-full text-center">
                    <button onclick="pressDigit('1')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-lg font-bold text-slate-800 leading-none">1</span>
                        <span class="text-[8px] text-slate-400 font-normal leading-none mt-0.5">&bull;&bull;&bull;</span>
                    </button>
                    <button onclick="pressDigit('2')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-lg font-bold text-slate-800 leading-none">2</span>
                        <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">ABC</span>
                    </button>
                    <button onclick="pressDigit('3')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-lg font-bold text-slate-800 leading-none">3</span>
                        <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">DEF</span>
                    </button>

                    <button onclick="pressDigit('4')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-lg font-bold text-slate-800 leading-none">4</span>
                        <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">GHI</span>
                    </button>
                    <button onclick="pressDigit('5')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-lg font-bold text-slate-800 leading-none">5</span>
                        <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">JKL</span>
                    </button>
                    <button onclick="pressDigit('6')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-lg font-bold text-slate-800 leading-none">6</span>
                        <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">MNO</span>
                    </button>

                    <button onclick="pressDigit('7')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-lg font-bold text-slate-800 leading-none">7</span>
                        <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">PQRS</span>
                    </button>
                    <button onclick="pressDigit('8')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-lg font-bold text-slate-800 leading-none">8</span>
                        <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">TUV</span>
                    </button>
                    <button onclick="pressDigit('9')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-lg font-bold text-slate-800 leading-none">9</span>
                        <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">WXYZ</span>
                    </button>

                    <button onclick="pressDigit('*')" class="dial-key h-12 flex items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-xl font-bold text-slate-800">*</span>
                    </button>
                    <button onclick="pressDigit('0')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-lg font-bold text-slate-800 leading-none">0</span>
                        <span class="text-[9px] text-slate-400 font-normal leading-none mt-0.5">+</span>
                    </button>
                    <button onclick="pressDigit('#')" class="dial-key h-12 flex items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                        <span class="text-lg font-bold text-slate-800">#</span>
                    </button>
                </div>

                <!-- Bottom Actions: Transcribe & Green Call Button (Exact RingCentral) -->
                <div class="flex items-center justify-center gap-8 mt-5">
                    <!-- Transcribe / AI Button -->
                    <button onclick="toggleTranscribeMode()" id="transcribeBtn" class="flex flex-col items-center text-slate-500 hover:text-blue-600 transition" title="Bilingual Real-Time AI Transcription">
                        <div class="w-10 h-10 rounded-full border border-slate-300 flex items-center justify-center text-slate-600 bg-white hover:bg-slate-50 shadow-xs">
                            <span class="text-base font-black">≡</span>
                        </div>
                        <span class="text-[10px] font-medium text-slate-500 mt-1">Transcribe</span>
                    </button>

                    <!-- Green Circular Call Button -->
                    <button onclick="makeCallFromKeypad()" class="w-14 h-14 rounded-full bg-[#22c55e] hover:bg-[#16a34a] text-white flex items-center justify-center shadow-lg shadow-emerald-500/25 transition transform active:scale-95 cursor-pointer" title="Call">
                        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56a.977.977 0 00-1.01.24l-2.2 2.2a15.053 15.053 0 01-6.59-6.59l2.2-2.21a.96.96 0 00.25-1.01A11.36 11.36 0 018.5 3.93c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.55c0-.55-.45-1-.99-1z"/></svg>
                    </button>
                </div>
            </div>'''

new_dialer_body = '''            <!-- VIEW A: Keypad Dial View -->
            <div id="keypadDialView" class="flex-1 flex flex-col">
                <!-- Enter a name or number Input -->
                <div class="px-5 pt-2 pb-1">
                    <div class="relative flex items-center">
                        <input id="keypadNumberInput" type="tel" placeholder="Enter a name or number" class="w-full bg-transparent border-b border-slate-200 focus:border-blue-600 py-2 pr-8 text-sm font-semibold text-slate-800 placeholder-slate-400 outline-none transition font-sans">
                        <button onclick="clearKeypadDigit()" class="absolute right-0 text-slate-400 hover:text-slate-700 p-1 text-sm transition" title="Clear">
                            ⌫
                        </button>
                    </div>
                </div>

                <!-- Numeric Keypad (RingCentral Minimalist Style) -->
                <div class="px-6 py-2 flex-1 flex flex-col justify-center">
                    <div class="grid grid-cols-3 gap-y-3 gap-x-4 max-w-[220px] mx-auto w-full text-center">
                        <button onclick="pressDigit('1')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-lg font-bold text-slate-800 leading-none">1</span>
                            <span class="text-[8px] text-slate-400 font-normal leading-none mt-0.5">&bull;&bull;&bull;</span>
                        </button>
                        <button onclick="pressDigit('2')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-lg font-bold text-slate-800 leading-none">2</span>
                            <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">ABC</span>
                        </button>
                        <button onclick="pressDigit('3')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-lg font-bold text-slate-800 leading-none">3</span>
                            <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">DEF</span>
                        </button>

                        <button onclick="pressDigit('4')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-lg font-bold text-slate-800 leading-none">4</span>
                            <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">GHI</span>
                        </button>
                        <button onclick="pressDigit('5')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-lg font-bold text-slate-800 leading-none">5</span>
                            <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">JKL</span>
                        </button>
                        <button onclick="pressDigit('6')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-lg font-bold text-slate-800 leading-none">6</span>
                            <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">MNO</span>
                        </button>

                        <button onclick="pressDigit('7')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-lg font-bold text-slate-800 leading-none">7</span>
                            <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">PQRS</span>
                        </button>
                        <button onclick="pressDigit('8')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-lg font-bold text-slate-800 leading-none">8</span>
                            <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">TUV</span>
                        </button>
                        <button onclick="pressDigit('9')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-lg font-bold text-slate-800 leading-none">9</span>
                            <span class="text-[8px] text-slate-400 font-bold leading-none mt-0.5">WXYZ</span>
                        </button>

                        <button onclick="pressDigit('*')" class="dial-key h-12 flex items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-xl font-bold text-slate-800">*</span>
                        </button>
                        <button onclick="pressDigit('0')" class="dial-key h-12 flex flex-col items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-lg font-bold text-slate-800 leading-none">0</span>
                            <span class="text-[9px] text-slate-400 font-normal leading-none mt-0.5">+</span>
                        </button>
                        <button onclick="pressDigit('#')" class="dial-key h-12 flex items-center justify-center rounded-2xl hover:bg-slate-100/80 cursor-pointer">
                            <span class="text-lg font-bold text-slate-800">#</span>
                        </button>
                    </div>

                    <!-- Bottom Actions: Transcribe & Green Call Button (Exact RingCentral) -->
                    <div class="flex items-center justify-center gap-8 mt-5">
                        <!-- Transcribe / AI Button -->
                        <button onclick="toggleTranscribeMode()" id="transcribeBtn" class="flex flex-col items-center text-slate-500 hover:text-blue-600 transition" title="Bilingual Real-Time AI Transcription">
                            <div class="w-10 h-10 rounded-full border border-slate-300 flex items-center justify-center text-slate-600 bg-white hover:bg-slate-50 shadow-xs">
                                <span class="text-base font-black">≡</span>
                            </div>
                            <span class="text-[10px] font-medium text-slate-500 mt-1">Transcribe</span>
                        </button>

                        <!-- Green Circular Call Button (Direct Calling - ZERO Popups!) -->
                        <button onclick="makeCallFromKeypad()" class="w-14 h-14 rounded-full bg-[#22c55e] hover:bg-[#16a34a] text-white flex items-center justify-center shadow-lg shadow-emerald-500/25 transition transform active:scale-95 cursor-pointer" title="Direct 1-Click Call">
                            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56a.977.977 0 00-1.01.24l-2.2 2.2a15.053 15.053 0 01-6.59-6.59l2.2-2.21a.96.96 0 00.25-1.01A11.36 11.36 0 018.5 3.93c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.55c0-.55-.45-1-.99-1z"/></svg>
                        </button>
                    </div>
                </div>
            </div>

            <!-- VIEW B: Active Live In-Call Screen (ZERO Popups - Direct Phone Experience) -->
            <div id="keypadActiveCallView" class="hidden flex-1 flex flex-col justify-between py-6 px-5 text-center bg-gradient-to-b from-slate-50 to-white">
                <div>
                    <div class="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Connected Line</div>
                    <div class="text-xs font-bold text-slate-700 mt-0.5">Amestx (844) 826-3789</div>

                    <!-- Callee Number -->
                    <div id="activeCallNumberDisplay" class="text-2xl font-black text-slate-900 mt-6 tracking-tight font-mono">
                        (832) 390-8863
                    </div>

                    <!-- Active Pulsing Call Badge -->
                    <div class="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                        <span id="activeCallStatusText">HD Voice Active</span>
                    </div>

                    <!-- Live Duration Timer -->
                    <div id="activeCallTimer" class="mt-3 text-sm font-mono font-bold text-slate-600">
                        00:00
                    </div>

                    <!-- AI Translation Live Indicator -->
                    <div class="mt-4 p-3 rounded-2xl bg-indigo-50 border border-indigo-100 text-left">
                        <div class="flex items-center justify-between text-xs font-bold text-indigo-900 mb-1">
                            <span>✨ Bilingual AI Bridge</span>
                            <span class="text-[10px] bg-indigo-600 text-white px-2 py-0.2 rounded-full font-black">LIVE</span>
                        </div>
                        <p class="text-[11px] text-indigo-700">Spanish ↔ English translation is active on this call in real time.</p>
                    </div>
                </div>

                <!-- In-Call Quick Controls -->
                <div class="space-y-4">
                    <div class="flex items-center justify-center gap-4">
                        <button onclick="toggleInCallMute(this)" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Mute Microphone">
                            🎤
                        </button>
                        <button onclick="switchToTextMessenger()" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Send SMS while on call">
                            💬
                        </button>
                        <button onclick="switchRightTab('forwarding')" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Forwarding Options">
                            ⚡
                        </button>
                    </div>

                    <!-- Red Circular End Call Button -->
                    <div class="flex justify-center">
                        <button onclick="endActiveCall()" class="w-14 h-14 rounded-full bg-rose-600 hover:bg-rose-700 active:scale-95 text-white flex items-center justify-center shadow-lg shadow-rose-600/30 transition cursor-pointer" title="End Call">
                            <svg class="w-6 h-6 transform rotate-[135deg]" fill="currentColor" viewBox="0 0 24 24"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56a.977.977 0 00-1.01.24l-2.2 2.2a15.053 15.053 0 01-6.59-6.59l2.2-2.21a.96.96 0 00.25-1.01A11.36 11.36 0 018.5 3.93c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.55c0-.55-.45-1-.99-1z"/></svg>
                        </button>
                    </div>
                </div>
            </div>'''

if old_dialer_body in content:
    content = content.replace(old_dialer_body, new_dialer_body)
    print("Replaced dialer body with active in-call screen!")
else:
    print("Dialer body exact string not found!")

# 3. Add Text tab button in Sub Header Tabs
old_tabs = '''                    <button onclick="switchRightTab('favorites')" id="tabFavorites" class="px-3 py-1 text-slate-600 hover:text-slate-900 rounded-lg text-xs font-semibold transition">
                        Favorites
                    </button>'''

new_tabs = '''                    <button onclick="switchRightTab('text')" id="tabText" class="px-3 py-1 text-slate-600 hover:text-slate-900 rounded-lg text-xs font-semibold transition flex items-center gap-1.5">
                        <span>Text (SMS)</span>
                        <span class="text-[9px] bg-blue-100 text-blue-700 font-extrabold px-1.5 py-0.2 rounded-full">AI</span>
                    </button>
                    <button onclick="switchRightTab('favorites')" id="tabFavorites" class="px-3 py-1 text-slate-600 hover:text-slate-900 rounded-lg text-xs font-semibold transition">
                        Favorites
                    </button>'''

if old_tabs in content:
    content = content.replace(old_tabs, new_tabs)
    print("Added Text tab button to header tabs!")
else:
    print("Tabs exact string not found!")

# 4. Add VIEW 4: TEXT / 2-WAY SMS MESSENGER right before Favorites view
old_fav_view = '            <!-- VIEW 3: FAVORITES -->'
new_text_view = '''            <!-- VIEW 4: INTERACTIVE 2-WAY SMS & TEXT MESSENGER (ZERO POPUPS) -->
            <div id="viewText" class="hidden flex-1 flex flex-col h-full bg-slate-50">
                <!-- Text Messenger Header -->
                <div class="p-4 bg-white border-b border-slate-200 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-md shadow-blue-500/20">
                            💬
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <span class="text-xs font-extrabold text-slate-900">SMS to:</span>
                                <input id="smsRecipientInput" type="tel" value="8323908863" placeholder="Enter cell number..." class="font-mono text-sm font-bold text-blue-700 bg-slate-50 px-2 py-0.5 rounded-lg border border-slate-200 focus:outline-none focus:border-blue-500">
                            </div>
                            <div class="text-[11px] text-slate-500 font-medium">From Amestx Business Line: <strong class="text-slate-800">(844) 826-3789</strong></div>
                        </div>
                    </div>

                    <!-- AI Translation Badge -->
                    <div class="flex items-center gap-2 bg-purple-50 text-purple-700 border border-purple-200 px-3 py-1 rounded-full text-xs font-bold">
                        <span class="w-2 h-2 rounded-full bg-purple-600 animate-pulse"></span>
                        <span>Spanish AI Translation: ACTIVE</span>
                    </div>
                </div>

                <!-- Chat Messages Stream -->
                <div id="smsChatStream" class="flex-1 p-6 space-y-4 overflow-y-auto custom-scrollbar">
                    <!-- Received from client -->
                    <div class="flex items-start gap-3 max-w-lg">
                        <div class="w-8 h-8 rounded-full bg-slate-200 text-slate-700 font-bold text-xs flex items-center justify-center flex-shrink-0">
                            CL
                        </div>
                        <div>
                            <div class="bg-white p-3.5 rounded-2xl rounded-tl-none shadow-xs border border-slate-200 text-xs text-slate-800 leading-relaxed">
                                Good morning! Can you confirm if our subcontractor crew can start at highway 290 site tomorrow?
                            </div>
                            <div class="text-[10px] text-slate-400 mt-1 font-mono">Today, 9:15 AM &bull; SMS received on (844) 826-3789</div>
                        </div>
                    </div>

                    <!-- Sent by Amestx with Spanish Translation -->
                    <div class="flex items-start gap-3 max-w-lg ml-auto flex-row-reverse">
                        <div class="w-8 h-8 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center flex-shrink-0">
                            AV
                        </div>
                        <div class="text-right">
                            <div class="bg-blue-600 text-white p-3.5 rounded-2xl rounded-tr-none shadow-xs text-xs text-left leading-relaxed">
                                <div>Yes, the TxDOT clearance is approved. Crew is scheduled for 7:00 AM.</div>
                                <div class="mt-2 pt-2 border-t border-blue-500/60 text-[11px] text-blue-100 flex items-center gap-1 font-medium">
                                    <span>🌐 AI Spanish Auto-Sent:</span>
                                    <em>"Sí, la autorización de TxDOT está aprobada. La cuadrilla está programada para las 7:00 AM."</em>
                                </div>
                            </div>
                            <div class="text-[10px] text-slate-400 mt-1 font-mono">Today, 9:18 AM &bull; Delivered via Amestx Line</div>
                        </div>
                    </div>
                </div>

                <!-- SMS Composer Bar -->
                <div class="p-4 bg-white border-t border-slate-200">
                    <form onsubmit="handleSendSms(event)" class="flex items-center gap-3">
                        <input id="smsMessageInput" type="text" placeholder="Type text message to client or crew (instant Spanish translation)..." class="flex-1 px-4 py-3 bg-slate-50 border border-slate-300 rounded-2xl text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition">
                        <button type="submit" class="px-5 py-3 bg-blue-600 hover:bg-blue-700 active:scale-95 text-white text-xs font-bold rounded-2xl transition shadow-md shadow-blue-500/20 flex items-center gap-1.5 flex-shrink-0">
                            <span>Send SMS</span>
                            <span>&rarr;</span>
                        </button>
                    </form>
                    <div class="flex items-center justify-between text-[11px] text-slate-500 mt-2 px-1">
                        <span>📲 2-way client texting with zero alert popups</span>
                        <span class="text-emerald-600 font-bold">✓ Forwarded to personal cell (832) 837-9801</span>
                    </div>
                </div>
            </div>

            <!-- VIEW 3: FAVORITES -->'''

if old_fav_view in content:
    content = content.replace(old_fav_view, new_text_view)
    print("Added VIEW 4: Text Messenger!")
else:
    print("Favorites view exact string not found!")

# 5. Replace JavaScript alert logic with pure smooth zero-popup flows
old_js_actions = '''        function testCallForwardingSimulation() {
            alert(`🔔 SIMULATED INCOMING CALL:
From: +1 (512) 472-8819 (Austin Contractor)
Calling Amestx Number: (844) 826-3789

Routing: FORWARDED TO YOUR CELL PHONE ${fwdState.phone}
Ring Strategy: ${fwdState.strategy.toUpperCase()}
Bilingual AI Bridge: ${fwdState.ai ? 'ACTIVE (Spanish ↔ English)' : 'Off'}

Your personal cell phone is now ringing!`);
        }'''

new_js_actions = '''        function testCallForwardingSimulation() {
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

if old_js_actions in content:
    content = content.replace(old_js_actions, new_js_actions)
    print("Replaced simulation alert with smooth zero-popup flow!")
else:
    print("Simulation alert not found exactly.")

old_make_call = '''        function makeCallFromKeypad() {
            const inp = document.getElementById('keypadNumberInput');
            const num = inp ? inp.value.trim() : '';
            if (!num) {
                alert("Please enter a telephone number to dial.");
                return;
            }
            alert(`📞 Calling ${num} from (844) 826-3789 with HD Voice...`);
        }'''

new_make_call = '''        let activeCallTimerInterval = null;
        let callSeconds = 0;

        function makeCallFromKeypad() {
            const inp = document.getElementById('keypadNumberInput');
            const num = inp ? inp.value.trim() : '';
            if (!num) {
                showNotification("⚠️ Please enter a telephone number to dial");
                if (inp) inp.focus();
                return;
            }
            // ZERO POPUPS! Start call directly
            startActiveCallScreen(num);
        }

        function startActiveCallScreen(num) {
            const dialView = document.getElementById('keypadDialView');
            const callView = document.getElementById('keypadActiveCallView');
            const numDisp = document.getElementById('activeCallNumberDisplay');
            const statusTxt = document.getElementById('activeCallStatusText');
            const timerDisp = document.getElementById('activeCallTimer');

            if (numDisp) numDisp.textContent = num;
            if (statusTxt) statusTxt.textContent = "Calling with HD Voice...";
            if (dialView) dialView.classList.add('hidden');
            if (callView) callView.classList.remove('hidden');

            // Pre-seed SMS recipient too so user can seamlessly text them
            const smsRecip = document.getElementById('smsRecipientInput');
            if (smsRecip) smsRecip.value = num;

            // Start timer
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
            }, 1000);

            showNotification(`📞 Connected to ${num} from (844) 826-3789`);
        }

        function endActiveCall() {
            if (activeCallTimerInterval) {
                clearInterval(activeCallTimerInterval);
                activeCallTimerInterval = null;
            }
            const dialView = document.getElementById('keypadDialView');
            const callView = document.getElementById('keypadActiveCallView');
            if (callView) callView.classList.add('hidden');
            if (dialView) dialView.classList.remove('hidden');

            showNotification("Call ended");
        }

        function toggleInCallMute(btn) {
            if (!btn) return;
            const isMuted = btn.classList.toggle('bg-rose-100');
            btn.classList.toggle('text-rose-700');
            showNotification(isMuted ? "🔇 Microphone Muted" : "🎤 Microphone Active");
        }

        function toggleAirAiAssistant() {
            showNotification("✨ Bilingual AI Translator: Active (Spanish ↔ English)");
        }

        function switchToTextMessenger() {
            // Get whatever number is currently in the keypad
            const kpNum = document.getElementById('keypadNumberInput');
            const smsRecip = document.getElementById('smsRecipientInput');
            if (kpNum && kpNum.value.trim() && smsRecip) {
                smsRecip.value = kpNum.value.trim();
            }
            switchRightTab('text');
            showNotification("💬 Opened Text & Client SMS");
        }

        function handleSendSms(e) {
            e.preventDefault();
            const inp = document.getElementById('smsMessageInput');
            const recip = document.getElementById('smsRecipientInput');
            const stream = document.getElementById('smsChatStream');
            if (!inp || !inp.value.trim()) return;

            const text = inp.value.trim();
            const toNum = recip ? recip.value.trim() : 'Client';

            // Add sent bubble
            const bubble = document.createElement('div');
            bubble.className = "flex items-start gap-3 max-w-lg ml-auto flex-row-reverse animate-in fade-in slide-in-from-bottom-2";
            bubble.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center flex-shrink-0">
                    AV
                </div>
                <div class="text-right">
                    <div class="bg-blue-600 text-white p-3.5 rounded-2xl rounded-tr-none shadow-xs text-xs text-left leading-relaxed">
                        <div>${text}</div>
                        <div class="mt-2 pt-2 border-t border-blue-500/60 text-[11px] text-blue-100 flex items-center gap-1 font-medium">
                            <span>🌐 AI Spanish Auto-Sent:</span>
                            <em>"Traducción automática enviada al cliente."</em>
                        </div>
                    </div>
                    <div class="text-[10px] text-slate-400 mt-1 font-mono">Just now &bull; Delivered via (844) 826-3789</div>
                </div>
            `;
            if (stream) {
                stream.appendChild(bubble);
                stream.scrollTop = stream.scrollHeight;
            }
            inp.value = '';

            // ZERO POPUPS - Smooth auto-fading confirmation
            showNotification(`✅ SMS delivered to ${toNum}`);
        }'''

if old_make_call in content:
    content = content.replace(old_make_call, new_make_call)
    print("Replaced makeCallFromKeypad with direct in-call engine!")
else:
    print("makeCallFromKeypad not found exactly!")

# Update switchRightTab to support 'text'
old_switch = "['hud', 'forwarding', 'favorites'].forEach(t => {"
new_switch = "['hud', 'forwarding', 'favorites', 'text'].forEach(t => {"
if old_switch in content:
    content = content.replace(old_switch, new_switch)
    print("Updated switchRightTab to support 'text'!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("voice-app.html successfully updated with ZERO POPUPS!")
