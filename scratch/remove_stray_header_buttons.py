file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''<body class="h-screen w-screen overflow-hidden flex flex-col bg-white antialiased select-none">
    
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

replacement = '<body class="h-screen w-screen overflow-hidden flex flex-col bg-white antialiased select-none">'

if target in text:
    text = text.replace(target, replacement)
    print("Cleanly removed leftover stray buttons above header!")
else:
    print("target not found")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("voice-app.html successfully cleaned!")
