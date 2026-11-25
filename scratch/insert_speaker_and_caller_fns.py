file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        function toggleInCallMute(btn) {
            if (!btn) return;
            const isMuted = btn.classList.toggle('bg-rose-100');
            btn.classList.toggle('text-rose-700');
            showNotification(isMuted ? "🔇 Microphone Muted" : "🎤 Microphone Active");
        }'''

replacement = '''        function toggleInCallMute(btn) {
            if (!btn) return;
            const isMuted = btn.classList.toggle('bg-rose-100');
            btn.classList.toggle('text-rose-700');
            showNotification(isMuted ? "🔇 Microphone Muted" : "🎤 Microphone Active");
        }

        // ==================== PHONE SPEAKER MUTE (Solves Voice Overlap / Echo) ====================
        let isPhoneSpeakerMuted = false;
        function toggleInCallSpeaker(btn) {
            isPhoneSpeakerMuted = !isPhoneSpeakerMuted;
            const targetBtn = btn || document.getElementById('inCallSpeakerBtn');
            const statusLabel = document.getElementById('inCallSpeakerStatus');

            if (isPhoneSpeakerMuted) {
                if (targetBtn) {
                    targetBtn.innerHTML = "🔇";
                    targetBtn.classList.add('bg-rose-100', 'text-rose-700');
                    targetBtn.classList.remove('bg-slate-100', 'text-slate-700');
                }
                if (statusLabel) {
                    statusLabel.textContent = "MUTED (Silent mode — speaker audio off)";
                    statusLabel.className = "text-rose-700 font-bold";
                }
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                }
                showNotification("🔇 Phone speaker muted (Silent mode — avoids voice overlap)");
            } else {
                if (targetBtn) {
                    targetBtn.innerHTML = "🔊";
                    targetBtn.classList.remove('bg-rose-100', 'text-rose-700');
                    targetBtn.classList.add('bg-slate-100', 'text-slate-700');
                }
                if (statusLabel) {
                    statusLabel.textContent = "ON (Normal)";
                    statusLabel.className = "text-emerald-700 font-bold";
                }
                showNotification("🔊 Phone speaker active");
            }
        }

        // ==================== CALLER ID SELECTION HANDLER ====================
        function handleCallerIdChange(val) {
            if (val === '__ADD_NEW__') {
                const select = document.getElementById('callerIdSelect');
                if (select) select.value = '18448263789';
                openPurchaseNumberModal();
            } else {
                showNotification("Caller ID active line: " + val);
            }
        }'''

if target in text:
    text = text.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully inserted toggleInCallSpeaker and handleCallerIdChange!")
else:
    print("Target toggleInCallMute not found")
