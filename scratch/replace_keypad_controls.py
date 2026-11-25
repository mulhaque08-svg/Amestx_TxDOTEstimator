file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('<!-- In-Call Quick Controls -->')
idx2 = text.find('<!-- Reachability Quick Bar at Bottom of Phone -->')

# Find the </div>\n            </div> right before Reachability
end_controls = text.rfind('</div>\n            </div>', idx1, idx2)
old_block = text[idx1:end_controls + len('</div>\n            </div>')]

new_block = '''<!-- State 1: Incoming Call Ringing Controls (Big Green Answer & Red Decline) -->
                <div id="incomingCallRingingControls" class="hidden space-y-4">
                    <div class="flex items-center justify-center gap-8 py-3">
                        <!-- Big Green Answer Button -->
                        <div class="flex flex-col items-center gap-2">
                            <button onclick="answerIncomingCall()" class="w-16 h-16 rounded-full bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white flex items-center justify-center shadow-xl shadow-emerald-500/40 transition transform hover:scale-105 cursor-pointer animate-bounce" title="Answer Call">
                                <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56a.977.977 0 00-1.01.24l-2.2 2.2a15.053 15.053 0 01-6.59-6.59l2.2-2.21a.96.96 0 00.25-1.01A11.36 11.36 0 018.5 3.93c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.55c0-.55-.45-1-.99-1z"/></svg>
                            </button>
                            <span class="text-xs font-black text-emerald-700 tracking-wide uppercase">Answer</span>
                        </div>

                        <!-- Big Red Decline Button -->
                        <div class="flex flex-col items-center gap-2">
                            <button onclick="declineIncomingCall()" class="w-16 h-16 rounded-full bg-rose-600 hover:bg-rose-700 active:scale-95 text-white flex items-center justify-center shadow-xl shadow-rose-600/40 transition transform hover:scale-105 cursor-pointer" title="Decline Call">
                                <svg class="w-8 h-8 transform rotate-[135deg]" fill="currentColor" viewBox="0 0 24 24"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56a.977.977 0 00-1.01.24l-2.2 2.2a15.053 15.053 0 01-6.59-6.59l2.2-2.21a.96.96 0 00.25-1.01A11.36 11.36 0 018.5 3.93c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.55c0-.55-.45-1-.99-1z"/></svg>
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
                            <svg class="w-6 h-6 transform rotate-[135deg]" fill="currentColor" viewBox="0 0 24 24"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56a.977.977 0 00-1.01.24l-2.2 2.2a15.053 15.053 0 01-6.59-6.59l2.2-2.21a.96.96 0 00.25-1.01A11.36 11.36 0 018.5 3.93c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.55c0-.55-.45-1-.99-1z"/></svg>
                        </button>
                    </div>
                </div>
            </div>'''

print("Found old_block length:", len(old_block))
text = text[:idx1] + new_block + text[idx1 + len(old_block):]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated keypadActiveCallView with Answer/Decline buttons!")
