import os, re

file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace callerIdSelect with strictly the Master Line + Add New option
old_caller_select = '''<select id="callerIdSelect" class="w-full bg-transparent hover:bg-slate-50 text-xs font-bold text-slate-800 outline-none cursor-pointer pr-2 py-1 border-b border-transparent hover:border-slate-300 transition">
                        <option value="18448263789">(844) 826-3789 (Toll-Free Nationwide)</option>
                        <option value="12109424238">(210) 942-4238 (San Antonio, TX)</option>
                        <option value="15125550192">(512) 555-0192 (Austin, TX)</option>
                        <option value="17135550144">(713) 555-0144 (Houston, TX)</option>
                    </select>'''

new_caller_select = '''<select id="callerIdSelect" onchange="handleCallerIdChange(this.value)" class="w-full bg-transparent hover:bg-slate-50 text-xs font-bold text-slate-800 outline-none cursor-pointer pr-2 py-1 border-b border-transparent hover:border-slate-300 transition">
                        <option value="18448263789">🔒 (844) 826-3789 (Amestx Master Line • Active)</option>
                        <option value="__ADD_NEW__" class="text-blue-600 font-bold">+ Purchase &amp; Add New Line ($29/mo)...</option>
                    </select>'''

if old_caller_select in content:
    content = content.replace(old_caller_select, new_caller_select)
    print("Replaced callerIdSelect with secured Master Line only!")
else:
    print("old_caller_select not found directly, checking regex...")
    content = re.sub(
        r'<select id="callerIdSelect"[\s\S]*?</select>',
        new_caller_select,
        content
    )
    print("Regex replaced callerIdSelect!")

# 2. Add Speaker / Audio Mute Toggle to In-Call Controls in keypadActiveCallView
old_controls = '''                <!-- In-Call Quick Controls -->
                <div class="space-y-4">
                    <div class="flex items-center justify-center gap-4">
                        <button onclick="toggleInCallMute(this)" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Mute Microphone">
                            🎤
                        </button>
                        <button onclick="switchToTextMessenger()" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="2-Way Text / SMS">
                            💬
                        </button>
                        <button onclick="toggleAirAiAssistant()" class="w-11 h-11 rounded-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 flex items-center justify-center text-sm font-bold transition" title="Bilingual AI Assistant">
                            ⚡
                        </button>
                    </div>'''

new_controls = '''                <!-- In-Call Quick Controls -->
                <div class="space-y-4">
                    <div class="flex items-center justify-center gap-3">
                        <!-- Mic Mute Button -->
                        <button id="inCallMicBtn" onclick="toggleInCallMute(this)" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Mute/Unmute Microphone">
                            🎤
                        </button>
                        <!-- Phone Speaker Mute Toggle (Solves voice overlap / loud echo) -->
                        <button id="inCallSpeakerBtn" onclick="toggleInCallSpeaker(this)" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Phone Speaker: ON / Silent Mode">
                            🔊
                        </button>
                        <!-- 2-Way SMS Messenger -->
                        <button onclick="switchToTextMessenger()" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="2-Way Text / SMS">
                            💬
                        </button>
                        <!-- Bilingual AI Translation Toggle -->
                        <button onclick="toggleAirAiAssistant()" class="w-11 h-11 rounded-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 flex items-center justify-center text-sm font-bold transition" title="Bilingual AI Translation">
                            ✨
                        </button>
                    </div>
                    <div id="inCallSpeakerNote" class="text-[10px] text-slate-500 font-medium">
                        Speaker Audio: <span id="inCallSpeakerStatus" class="text-emerald-700 font-bold">ON (Normal)</span> • Click 🔊 to mute phone speaker
                    </div>'''

if old_controls in content:
    content = content.replace(old_controls, new_controls)
    print("Added Speaker Mute / Headphone Mode toggle to active call controls!")
else:
    print("old_controls exact match not found; looking for snippet...")
    content = re.sub(
        r'<!-- In-Call Quick Controls -->[\s\S]*?</div>\s*</div>\s*<!-- End Call Red Button -->',
        new_controls + '\n                </div>\n                <!-- End Call Red Button -->',
        content
    )
    print("Regex replaced in-call controls!")

# 3. Enhance JS for handleCallerIdChange, loadSavedPaidLines, toggleInCallSpeaker, and real calling
js_to_add = '''
        // ==================== PHONE SPEAKER MUTE (Solves Voice Overlap) ====================
        let isPhoneSpeakerMuted = false;
        function toggleInCallSpeaker(btn) {
            isPhoneSpeakerMuted = !isPhoneSpeakerMuted;
            const statusLabel = document.getElementById('inCallSpeakerStatus');
            const targetBtn = btn || document.getElementById('inCallSpeakerBtn');

            if (isPhoneSpeakerMuted) {
                if (targetBtn) {
                    targetBtn.innerHTML = "🔇";
                    targetBtn.classList.add('bg-amber-100', 'text-amber-800', 'border', 'border-amber-300');
                    targetBtn.classList.remove('bg-slate-100', 'text-slate-700');
                }
                if (statusLabel) {
                    statusLabel.textContent = "MUTED (Silent translation - no speaker voice echo)";
                    statusLabel.className = "text-amber-700 font-bold";
                }
                // Stop any browser speech synthesis if active
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                }
                showNotification("🔇 Phone speaker muted: Speech audio turned off (silent mode)");
            } else {
                if (targetBtn) {
                    targetBtn.innerHTML = "🔊";
                    targetBtn.classList.remove('bg-amber-100', 'text-amber-800', 'border', 'border-amber-300');
                    targetBtn.classList.add('bg-slate-100', 'text-slate-700');
                }
                if (statusLabel) {
                    statusLabel.textContent = "ON (Normal)";
                    statusLabel.className = "text-emerald-700 font-bold";
                }
                showNotification("🔊 Phone speaker restored: Audio active");
            }
        }

        // ==================== CALLER ID SELECTION & LOCAL STORAGE ====================
        function handleCallerIdChange(val) {
            if (val === '__ADD_NEW__') {
                const select = document.getElementById('callerIdSelect');
                if (select) select.value = '18448263789'; // Reset back to default
                openPurchaseNumberModal();
            } else {
                showNotification("Caller ID set to line: " + val);
            }
        }

        function loadSavedPaidLines() {
            try {
                const saved = JSON.parse(localStorage.getItem('amestx_paid_lines') || '[]');
                const select = document.getElementById('callerIdSelect');
                if (!select) return;

                saved.forEach(item => {
                    if (!paidLinesRegistry.includes(item.id)) {
                        paidLinesRegistry.push(item.id);
                    }
                    // Check if already in options
                    let exists = false;
                    for (let i = 0; i < select.options.length; i++) {
                        if (select.options[i].value === item.id) {
                            exists = true;
                            break;
                        }
                    }
                    if (!exists) {
                        const opt = document.createElement('option');
                        opt.value = item.id;
                        opt.textContent = `★ ${item.number} (${item.label.split(' ')[0]} • Active Line)`;
                        // Insert before the last option (+ Purchase & Add New Line)
                        select.insertBefore(opt, select.options[select.options.length - 1]);
                    }
                });
            } catch (err) {
                console.warn("Could not load saved lines:", err);
            }
        }

        // Auto-run on DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                loadSavedPaidLines();
                initTwilioVoice();
            });
        } else {
            loadSavedPaidLines();
            initTwilioVoice();
        }
'''

# Add js_to_add before the closing </script> tag
if 'function toggleInCallSpeaker' not in content:
    content = content.replace('</script>\n</body>', js_to_add + '\n</script>\n</body>')
    print("Added toggleInCallSpeaker and loadSavedPaidLines JS!")

# 4. Make sure handleProcessPayment saves to localStorage
old_payment_storage = '''                if (pendingCheckoutId) paidLinesRegistry.push(pendingCheckoutId);'''
new_payment_storage = '''                if (pendingCheckoutId) {
                    paidLinesRegistry.push(pendingCheckoutId);
                    try {
                        const saved = JSON.parse(localStorage.getItem('amestx_paid_lines') || '[]');
                        saved.push({ id: pendingCheckoutId, number: pendingCheckoutNumber, label: pendingCheckoutLabel });
                        localStorage.setItem('amestx_paid_lines', JSON.stringify(saved));
                    } catch(e) {}
                }'''

if old_payment_storage in content and 'localStorage.setItem(\'amestx_paid_lines\'' not in content:
    content = content.replace(old_payment_storage, new_payment_storage)
    print("Added persistent localStorage saving to handleProcessPayment!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("voice-app.html successfully perfected!")
