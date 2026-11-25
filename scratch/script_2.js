
        // Load data on start
        let fwdState = {
            enabled: true,
            phone: "(832) 837-9801",
            backup: "",
            strategy: "simultaneous",
            ai: true,
            sms: true
        };

        function initApp() {
            try {
                const stored = localStorage.getItem('amestx_call_forwarding');
                if (stored) {
                    const parsed = JSON.parse(stored);
                    fwdState.enabled = parsed.enabled !== false;
                    fwdState.phone = parsed.primaryPhone || parsed.phone || fwdState.phone;
                    fwdState.backup = parsed.backupPhone || parsed.backup || "";
                    fwdState.strategy = parsed.ringStrategy || parsed.strategy || "simultaneous";
                    fwdState.ai = parsed.aiTranslationEnabled !== false;
                    fwdState.sms = parsed.forwardSms !== false;
                }
            } catch(e) {}

            // Populate UI
            const inp = document.getElementById('forwardPhoneInput');
            const bk = document.getElementById('backupPhoneInput');
            const tog = document.getElementById('mainForwardToggle');
            const aiTog = document.getElementById('aiBridgeToggle');
            const smsTog = document.getElementById('smsForwardToggle');
            const topDisp = document.getElementById('topForwardingNumberDisplay');
            const kpDisp = document.getElementById('keypadForwardStatus');

            if (inp) inp.value = fwdState.phone;
            if (bk) bk.value = fwdState.backup;
            if (tog) tog.checked = fwdState.enabled;
            if (aiTog) aiTog.checked = fwdState.ai;
            if (smsTog) smsTog.checked = fwdState.sms;
            if (topDisp) topDisp.textContent = fwdState.enabled ? `ACTIVE → ${fwdState.phone}` : "DISABLED";
            if (kpDisp) kpDisp.textContent = fwdState.enabled ? `Mobile ${fwdState.phone}` : "Off";

            const radios = document.getElementsByName('ringStrategyRadio');
            for (let r of radios) {
                r.checked = (r.value === fwdState.strategy);
            }
        }

        function toggleForwarding(active) {
            fwdState.enabled = active;
            const lbl = document.getElementById('mainForwardToggleText');
            const topDisp = document.getElementById('topForwardingNumberDisplay');
            const kpDisp = document.getElementById('keypadForwardStatus');

            if (lbl) {
                lbl.textContent = active ? "ACTIVE • Forwarding ON" : "PAUSED • Desktop Only";
                lbl.className = active ? "text-xs font-black text-emerald-300 mt-1.5" : "text-xs font-bold text-slate-400 mt-1.5";
            }
            if (topDisp) topDisp.textContent = active ? `ACTIVE → ${fwdState.phone}` : "DISABLED";
            if (kpDisp) kpDisp.textContent = active ? `Mobile ${fwdState.phone}` : "Off";

            saveForwardingConfig(false);
            showNotification(active ? "Call Forwarding Active! Your cell will ring." : "Forwarding Paused (Desktop Only)");
        }

        function saveRingStrategy(val) {
            fwdState.strategy = val;
            saveForwardingConfig(false);
            showNotification(`Strategy: ${val.toUpperCase()}`);
        }

        function saveForwardingConfig(showToast = true) {
            const inp = document.getElementById('forwardPhoneInput');
            const bk = document.getElementById('backupPhoneInput');
            const aiTog = document.getElementById('aiBridgeToggle');
            const smsTog = document.getElementById('smsForwardToggle');

            if (inp) fwdState.phone = inp.value.trim();
            if (bk) fwdState.backup = bk.value.trim();
            if (aiTog) fwdState.ai = aiTog.checked;
            if (smsTog) fwdState.sms = smsTog.checked;

            const configToStore = {
                enabled: fwdState.enabled,
                primaryPhone: fwdState.phone,
                backupPhone: fwdState.backup,
                ringStrategy: fwdState.strategy,
                aiTranslationEnabled: fwdState.ai,
                forwardSms: fwdState.sms
            };
            localStorage.setItem('amestx_call_forwarding', JSON.stringify(configToStore));

            const topDisp = document.getElementById('topForwardingNumberDisplay');
            const kpDisp = document.getElementById('keypadForwardStatus');
            if (topDisp) topDisp.textContent = fwdState.enabled ? `ACTIVE → ${fwdState.phone}` : "DISABLED";
            if (kpDisp) kpDisp.textContent = fwdState.enabled ? `Mobile ${fwdState.phone}` : "Off";

            if (showToast) showNotification("Forwarding settings saved successfully!");
        }

        function testCallForwardingSimulation() {
            // ZERO POPUPS - In-app live simulation
            showNotification(`🔔 Incoming Call from (512) 472-8819 → Forwarding to your cell ${fwdState.phone}!`);
            
            // Show incoming call banner in the dialer
            const inp = document.getElementById('keypadNumberInput');
            if (inp) inp.value = '+1 (512) 472-8819';
            
            // Trigger in-call state after 1 second
            setTimeout(() => {
                startActiveCallScreen('+1 (512) 472-8819');
            }, 1000);
        }

        function switchRightTab(tab) {
            ['hud', 'forwarding', 'favorites', 'text'].forEach(t => {
                const btn = document.getElementById(`tab${t.charAt(0).toUpperCase() + t.slice(1)}`);
                const view = document.getElementById(`view${t.charAt(0).toUpperCase() + t.slice(1)}`);
                if (t === tab) {
                    if (btn) btn.className = "px-3 py-1 bg-blue-50 text-blue-700 rounded-lg text-xs font-bold transition";
                    if (view) view.classList.remove('hidden');
                } else {
                    if (btn) btn.className = "px-3 py-1 text-slate-600 hover:text-slate-900 rounded-lg text-xs font-semibold transition";
                    if (view) view.classList.add('hidden');
                }
            });
        }

        function switchPhoneTab(tab) {
            ['keypad', 'calls', 'voicemail', 'recordings'].forEach(t => {
                const btn = document.getElementById(`tabPhone${t.charAt(0).toUpperCase() + t.slice(1)}`);
                if (btn) {
                    if (t === tab) {
                        btn.className = "py-2.5 px-2 text-blue-600 border-b-2 border-blue-600 font-bold transition";
                    } else {
                        btn.className = "py-2.5 px-2 hover:text-slate-900 transition";
                    }
                }
            });
        }

        function pressDigit(d) {
            const inp = document.getElementById('keypadNumberInput');
            if (inp) inp.value += d;
        }

        function clearKeypadDigit() {
            const inp = document.getElementById('keypadNumberInput');
            if (inp) inp.value = inp.value.slice(0, -1);
        }

        function toggleTranscribeMode() {
            const btn = document.getElementById('transcribeBtn');
            if (btn) {
                btn.classList.toggle('text-blue-600');
                showNotification("Bilingual AI Voice Transcription Toggled");
            }
        }

        let activeCallTimerInterval = null;
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

        function formatPhoneNumber(raw) {
            const digits = (raw || '').replace(/\D/g, '');
            if (digits.length === 10) {
                return () -;
            } else if (digits.length === 11 && digits.startsWith('1')) {
                return +1 () -;
            }
            return raw;
        }

        function startActiveCallScreen(num) {
            const formatted = formatPhoneNumber(num);
            const dialView = document.getElementById('keypadDialView');
            const callView = document.getElementById('keypadActiveCallView');
            const numDisp = document.getElementById('activeCallNumberDisplay');
            const statusTxt = document.getElementById('activeCallStatusText');
            const timerDisp = document.getElementById('activeCallTimer');

            if (numDisp) numDisp.textContent = formatted;
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
        }

        function showNotification(msg) {
            const toast = document.getElementById('toastNotification');
            const txt = document.getElementById('toastMessage');
            if (!toast) return;
            if (txt) txt.textContent = msg;
            toast.classList.remove('translate-y-24', 'opacity-0');
            toast.classList.add('translate-y-0', 'opacity-100');
            setTimeout(() => {
                toast.classList.remove('translate-y-0', 'opacity-100');
                toast.classList.add('translate-y-24', 'opacity-0');
            }, 2500);
        }

        function handleLogout() {
            if (confirm("Sign out of Amestx Voice App?")) {
                localStorage.removeItem('amestx_subscribed');
                window.location.href = "voice.html";
            }
        }

        window.addEventListener('DOMContentLoaded', initApp);
    