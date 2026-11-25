import re

file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Floating Banner right after <body>
floating_banner_html = '''    <!-- Floating Incoming Call Banner (Visible Anywhere on Screen) -->
    <div id="incomingCallFloatingBanner" class="hidden fixed top-6 left-1/2 -translate-x-1/2 z-50 bg-[#0d163a] text-white px-6 py-4 rounded-3xl shadow-2xl border-2 border-emerald-500/50 flex items-center gap-6 animate-in slide-in-from-top duration-300">
        <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xl shadow-lg shadow-emerald-500/40 animate-bounce">
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56a.977.977 0 00-1.01.24l-2.2 2.2a15.053 15.053 0 01-6.59-6.59l2.2-2.21a.96.96 0 00.25-1.01A11.36 11.36 0 018.5 3.93c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.55c0-.55-.45-1-.99-1z"/></svg>
            </div>
            <div>
                <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                    <span class="text-[11px] font-bold text-emerald-300 uppercase tracking-widest">Incoming Call • (844) 826-3789</span>
                </div>
                <div id="floatingBannerCallerNumber" class="text-lg font-black text-white font-mono tracking-tight mt-0.5">+1 (832) 390-8863</div>
            </div>
        </div>
        <div class="flex items-center gap-2.5">
            <button onclick="answerIncomingCall()" class="px-5 py-2.5 rounded-2xl bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white text-xs font-black shadow-lg shadow-emerald-500/30 flex items-center gap-1.5 transition cursor-pointer">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                <span>Answer Call</span>
            </button>
            <button onclick="declineIncomingCall()" class="px-4 py-2.5 rounded-2xl bg-rose-600 hover:bg-rose-700 active:scale-95 text-white text-xs font-black shadow-lg shadow-rose-600/30 flex items-center gap-1.5 transition cursor-pointer">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                <span>Decline</span>
            </button>
        </div>
    </div>'''

if 'id="incomingCallFloatingBanner"' not in content:
    content = content.replace('<body class="bg-[#f0f3f8] text-slate-900 font-sans min-h-screen flex flex-col justify-between">',
                              '<body class="bg-[#f0f3f8] text-slate-900 font-sans min-h-screen flex flex-col justify-between">\n' + floating_banner_html)
    print("Added floating incoming call banner!")

# 2. In keypadActiveCallView, update controls area to support BOTH Incoming (Answer + Decline) and Connected (In-Call controls + End Call)
old_bottom_controls = '''                <!-- In-Call Quick Controls -->
                <div class="space-y-4">
                    <div class="flex items-center justify-center gap-3">
                        <button id="inCallMicBtn" onclick="toggleInCallMute(this)" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Mute/Unmute Microphone">
                            🎤
                        </button>
                        <button id="inCallSpeakerBtn" onclick="toggleInCallSpeaker(this)" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Mute/Unmute Phone Speaker (Silent Mode)">
                            🔊
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
                            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08a.956.956 0 0 1 0-1.36C3.25 8.79 7.4 7 12 7s8.75 1.79 11.71 4.72c.38.38.38.98 0 1.36l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.1-.7-.28-.79-.73-1.68-1.36-2.66-1.85-.33-.16-.56-.51-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/></svg>
                        </button>
                    </div>
                </div>'''

new_bottom_controls = '''                <!-- State 1: Incoming Call Ringing Controls (Big Green Answer & Red Decline) -->
                <div id="incomingCallRingingControls" class="hidden space-y-4">
                    <div class="flex items-center justify-center gap-8 py-2">
                        <!-- Big Green Answer Button -->
                        <div class="flex flex-col items-center gap-1.5">
                            <button onclick="answerIncomingCall()" class="w-16 h-16 rounded-full bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white flex items-center justify-center shadow-xl shadow-emerald-500/40 transition transform hover:scale-105 cursor-pointer animate-bounce" title="Answer Call">
                                <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 24 24"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56a.977.977 0 00-1.01.24l-2.2 2.2a15.053 15.053 0 01-6.59-6.59l2.2-2.21a.96.96 0 00.25-1.01A11.36 11.36 0 018.5 3.93c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.55c0-.55-.45-1-.99-1z"/></svg>
                            </button>
                            <span class="text-xs font-black text-emerald-700 tracking-wide uppercase">Answer</span>
                        </div>

                        <!-- Big Red Decline Button -->
                        <div class="flex flex-col items-center gap-1.5">
                            <button onclick="declineIncomingCall()" class="w-16 h-16 rounded-full bg-rose-600 hover:bg-rose-700 active:scale-95 text-white flex items-center justify-center shadow-xl shadow-rose-600/40 transition transform hover:scale-105 cursor-pointer" title="Decline Call">
                                <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 24 24"><path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08a.956.956 0 0 1 0-1.36C3.25 8.79 7.4 7 12 7s8.75 1.79 11.71 4.72c.38.38.38.98 0 1.36l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.1-.7-.28-.79-.73-1.68-1.36-2.66-1.85-.33-.16-.56-.51-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/></svg>
                            </button>
                            <span class="text-xs font-black text-rose-700 tracking-wide uppercase">Decline</span>
                        </div>
                    </div>
                </div>

                <!-- State 2: In-Call Connected Controls (Active Outbound / Inbound Call) -->
                <div id="inCallConnectedControls" class="space-y-4">
                    <div class="flex items-center justify-center gap-3">
                        <button id="inCallMicBtn" onclick="toggleInCallMute(this)" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Mute/Unmute Microphone">
                            🎤
                        </button>
                        <button id="inCallSpeakerBtn" onclick="toggleInCallSpeaker(this)" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Mute/Unmute Phone Speaker (Silent Mode)">
                            🔊
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
                            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08a.956.956 0 0 1 0-1.36C3.25 8.79 7.4 7 12 7s8.75 1.79 11.71 4.72c.38.38.38.98 0 1.36l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.1-.7-.28-.79-.73-1.68-1.36-2.66-1.85-.33-.16-.56-.51-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/></svg>
                        </button>
                    </div>
                </div>'''

if old_bottom_controls in content:
    content = content.replace(old_bottom_controls, new_bottom_controls)
    print("Replaced in-call controls with dual Incoming (Answer/Decline) & Connected states!")
else:
    print("old_bottom_controls not found directly")

# 3. Update JavaScript for handleIncomingTwilioCall, answerIncomingCall, declineIncomingCall, playIncomingRingtone, etc.
old_incoming_js = '''        function handleIncomingTwilioCall(call) {
            activeTwilioCall = call;
            const fromNumber = (call.parameters && call.parameters.From) ? call.parameters.From : "+1 (512) 472-8819";
            showNotification(`📲 Incoming Call from ${fromNumber} → Forwarding to cell!`);
            startActiveCallScreen(fromNumber);

            call.on('disconnect', () => {
                endActiveCall();
            });
        }'''

new_incoming_js = '''        // ==================== INCOMING CALL HANDLING ====================
        let pendingIncomingCall = null;
        let ringtoneAudioCtx = null;
        let ringtoneTimer = null;

        function playIncomingRingtone() {
            try {
                if (!ringtoneAudioCtx) {
                    ringtoneAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
                }
                if (ringtoneAudioCtx.state === 'suspended') ringtoneAudioCtx.resume();
                
                const playBeep = () => {
                    if (!pendingIncomingCall) return;
                    const osc = ringtoneAudioCtx.createOscillator();
                    const gain = ringtoneAudioCtx.createGain();
                    osc.connect(gain);
                    gain.connect(ringtoneAudioCtx.destination);
                    osc.frequency.setValueAtTime(440, ringtoneAudioCtx.currentTime);
                    gain.gain.setValueAtTime(0.12, ringtoneAudioCtx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, ringtoneAudioCtx.currentTime + 1.2);
                    osc.start();
                    osc.stop(ringtoneAudioCtx.currentTime + 1.2);
                };
                playBeep();
                ringtoneTimer = setInterval(playBeep, 2500);
            } catch(e) {}
        }

        function stopIncomingRingtone() {
            if (ringtoneTimer) {
                clearInterval(ringtoneTimer);
                ringtoneTimer = null;
            }
        }

        function handleIncomingTwilioCall(call) {
            pendingIncomingCall = call;
            activeTwilioCall = call;
            const rawFrom = (call.parameters && call.parameters.From) ? call.parameters.From : "+1 (832) 390-8863";
            const formatted = formatPhoneNumber(rawFrom);

            playIncomingRingtone();

            const dialView = document.getElementById('keypadDialView');
            const callView = document.getElementById('keypadActiveCallView');
            const numDisp = document.getElementById('activeCallNumberDisplay');
            const statusTxt = document.getElementById('activeCallStatusText');
            const timerDisp = document.getElementById('activeCallTimer');
            const connectedControls = document.getElementById('inCallConnectedControls');
            const ringingControls = document.getElementById('incomingCallRingingControls');

            if (numDisp) numDisp.textContent = formatted;
            if (statusTxt) statusTxt.textContent = "🔔 Incoming Call Ringing...";
            if (timerDisp) timerDisp.textContent = "00:00";
            if (dialView) dialView.classList.add('hidden');
            if (callView) callView.classList.remove('hidden');

            // Show Green Answer / Red Decline buttons
            if (connectedControls) connectedControls.classList.add('hidden');
            if (ringingControls) ringingControls.classList.remove('hidden');

            // Also show the floating banner at top of page
            const banner = document.getElementById('incomingCallFloatingBanner');
            const bannerNum = document.getElementById('floatingBannerCallerNumber');
            if (bannerNum) bannerNum.textContent = formatted;
            if (banner) banner.classList.remove('hidden');

            showNotification(`📲 Incoming Call from ${formatted} on (844) 826-3789`);

            call.on('cancel', () => {
                stopIncomingRingtone();
                hideIncomingCallUI();
                showNotification(`Missed call from ${formatted}`);
            });

            call.on('disconnect', () => {
                stopIncomingRingtone();
                endActiveCall();
            });
        }

        function answerIncomingCall() {
            stopIncomingRingtone();
            hideIncomingCallFloatingBanner();

            if (pendingIncomingCall) {
                try {
                    pendingIncomingCall.accept();
                    activeTwilioCall = pendingIncomingCall;
                } catch(e) {
                    console.warn("Call accept error:", e);
                }
            }

            const statusTxt = document.getElementById('activeCallStatusText');
            if (statusTxt) statusTxt.textContent = "Connected • Inbound HD Voice Active";
            showNotification("✓ Inbound Call Connected!");

            // Switch to connected controls (Mute, Speaker, Red End Call)
            const connectedControls = document.getElementById('inCallConnectedControls');
            const ringingControls = document.getElementById('incomingCallRingingControls');
            if (ringingControls) ringingControls.classList.add('hidden');
            if (connectedControls) connectedControls.classList.remove('hidden');

            beginCallTimer();
        }

        function declineIncomingCall() {
            stopIncomingRingtone();
            hideIncomingCallFloatingBanner();

            if (pendingIncomingCall) {
                try {
                    pendingIncomingCall.reject();
                } catch(e) {}
                pendingIncomingCall = null;
            }
            if (activeTwilioCall) {
                try {
                    activeTwilioCall.disconnect();
                } catch(e) {}
                activeTwilioCall = null;
            }
            hideIncomingCallUI();
            showNotification("Call declined");
        }

        function hideIncomingCallUI() {
            hideIncomingCallFloatingBanner();
            const dialView = document.getElementById('keypadDialView');
            const callView = document.getElementById('keypadActiveCallView');
            const connectedControls = document.getElementById('inCallConnectedControls');
            const ringingControls = document.getElementById('incomingCallRingingControls');

            if (callView) callView.classList.add('hidden');
            if (dialView) dialView.classList.remove('hidden');
            if (ringingControls) ringingControls.classList.add('hidden');
            if (connectedControls) connectedControls.classList.remove('hidden');
        }

        function hideIncomingCallFloatingBanner() {
            const banner = document.getElementById('incomingCallFloatingBanner');
            if (banner) banner.classList.add('hidden');
        }'''

if old_incoming_js in content:
    content = content.replace(old_incoming_js, new_incoming_js)
    print("Updated handleIncomingTwilioCall with full answer/decline & ringtone functions!")
else:
    print("old_incoming_js not found directly")

# 4. In startActiveCallScreen (for outbound calls), ensure incomingCallRingingControls is hidden and inCallConnectedControls is shown
content = content.replace(
    '''            if (numDisp) numDisp.textContent = formatted;
            if (statusTxt) statusTxt.textContent = `Connecting to ${formatted}...`;
            if (dialView) dialView.classList.add('hidden');
            if (callView) callView.classList.remove('hidden');''',
    '''            if (numDisp) numDisp.textContent = formatted;
            if (statusTxt) statusTxt.textContent = `Connecting to ${formatted}...`;
            if (dialView) dialView.classList.add('hidden');
            if (callView) callView.classList.remove('hidden');

            // For outbound calls: show inCallConnectedControls, hide incomingCallRingingControls
            const connectedControls = document.getElementById('inCallConnectedControls');
            const ringingControls = document.getElementById('incomingCallRingingControls');
            if (ringingControls) ringingControls.classList.add('hidden');
            if (connectedControls) connectedControls.classList.remove('hidden');'''
)

# 5. In endActiveCall, also stop ringtone and hide banner
content = content.replace(
    '''        function endActiveCall() {
            if (activeTwilioCall) {''',
    '''        function endActiveCall() {
            stopIncomingRingtone();
            hideIncomingCallFloatingBanner();
            if (activeTwilioCall) {'''
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("voice-app.html successfully updated with Answer/Decline buttons and floating incoming call banner!")
