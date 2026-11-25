file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                    <div class="flex items-center justify-center gap-4">
                        <button onclick="toggleInCallMute(this)" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Mute Microphone">
                            🎤
                        </button>
                        <button onclick="switchToTextMessenger()" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Send SMS while on call">
                            💬
                        </button>'''

replacement = '''                    <div class="flex items-center justify-center gap-3">
                        <button id="inCallMicBtn" onclick="toggleInCallMute(this)" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Mute/Unmute Microphone">
                            🎤
                        </button>
                        <button id="inCallSpeakerBtn" onclick="toggleInCallSpeaker(this)" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Mute/Unmute Phone Speaker (Silent Mode)">
                            🔊
                        </button>
                        <button onclick="switchToTextMessenger()" class="w-11 h-11 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-sm font-bold transition" title="Send SMS while on call">
                            💬
                        </button>'''

if target in text:
    text = text.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Successfully added Speaker button to in-call view!')
else:
    print('Target not found for in-call buttons')
