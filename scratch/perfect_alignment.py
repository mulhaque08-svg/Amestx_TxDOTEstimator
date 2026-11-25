file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace animate-bounce with animate-pulse for perfect button alignment
text = text.replace('cursor-pointer animate-bounce" title="Answer Call"', 'cursor-pointer animate-pulse" title="Answer Call"')

# Check where floating banner is
if 'id="incomingCallFloatingBanner"' not in text:
    # Add floating banner right inside body
    idx = text.find('<body')
    idx_end = text.find('>', idx)
    banner_html = '''
    <!-- Floating Top Incoming Call Notification -->
    <div id="incomingCallFloatingBanner" class="hidden fixed top-5 left-1/2 -translate-x-1/2 z-50 bg-[#0d163a] text-white px-6 py-3.5 rounded-full shadow-2xl border-2 border-emerald-500/60 flex items-center gap-6 animate-in slide-in-from-top duration-200">
        <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-emerald-400 animate-ping"></span>
            <div>
                <div class="text-[10px] font-bold text-emerald-300 uppercase tracking-widest">Incoming Call • (844) 826-3789</div>
                <div id="floatingBannerCallerNumber" class="text-sm font-black text-white font-mono">+1 (832) 390-8863</div>
            </div>
        </div>
        <div class="flex items-center gap-2">
            <button onclick="answerIncomingCall()" class="px-4 py-1.5 rounded-full bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-black shadow-md shadow-emerald-500/30 flex items-center gap-1 transition cursor-pointer">
                <span>✓ Answer</span>
            </button>
            <button onclick="declineIncomingCall()" class="px-3.5 py-1.5 rounded-full bg-rose-600 hover:bg-rose-700 text-white text-xs font-black shadow-md shadow-rose-600/30 flex items-center gap-1 transition cursor-pointer">
                <span>✕ Decline</span>
            </button>
        </div>
    </div>'''
    text = text[:idx_end+1] + banner_html + text[idx_end+1:]
    print("Added incomingCallFloatingBanner!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Alignment and banner perfected!")
