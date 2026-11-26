import re

file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the floating top banner completely
floating_pattern = r'<!-- Floating (Top )?Incoming Call (Banner|Notification) -->\s*<div id="incomingCallFloatingBanner"[\s\S]*?</div>\s*</div>'
if re.search(floating_pattern, content):
    content = re.sub(floating_pattern, '', content)
    print("Removed floating header banner from top of page!")
else:
    print("Floating banner pattern not found, checking manual string search...")
    idx = content.find('id="incomingCallFloatingBanner"')
    if idx != -1:
        # find the end of this div
        idx_start = content.rfind('<div id="incomingCallFloatingBanner"', 0, idx + 40)
        idx_end = content.find('</div>\n    </div>', idx)
        if idx_end != -1:
            content = content[:idx_start] + content[idx_end + len('</div>\n    </div>'):]
            print("Manually removed floating banner!")

# 2. Update incomingCallRingingControls to place the Answering Box in the sidebar (Green Circle Area)
target_ringing_controls = '''                <!-- State 1: Incoming Call Ringing Controls (Big Green Answer & Red Decline) -->
                <div id="incomingCallRingingControls" class="hidden space-y-4">
                    <div class="flex items-center justify-center gap-8 py-3">
                        <!-- Big Green Answer Button -->
                        <div class="flex flex-col items-center gap-2">
                            <button onclick="answerIncomingCall()" class="w-16 h-16 rounded-full bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white flex items-center justify-center shadow-xl shadow-emerald-500/40 transition transform hover:scale-105 cursor-pointer animate-pulse" title="Answer Call">
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
                </div>'''

replacement_ringing_controls = '''                <!-- State 1: Incoming Call Ringing Controls & Box (Sidebar Position - Green Circle Area) -->
                <div id="incomingCallRingingControls" class="hidden space-y-4 my-2">
                    <!-- The Answering Box (Moved from Header to Sidebar) -->
                    <div id="incomingCallSidebarCard" class="p-4 rounded-2xl bg-[#0d163a] text-white shadow-xl border-2 border-emerald-500/50 text-left">
                        <div class="flex items-center justify-between mb-1.5">
                            <span class="flex items-center gap-1.5 text-[10px] font-extrabold text-emerald-400 uppercase tracking-widest">
                                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                                <span>INCOMING CALL</span>
                            </span>
                            <span class="text-[10px] font-bold text-blue-200 bg-blue-900/60 px-2 py-0.5 rounded-full font-mono">(844) 826-3789</span>
                        </div>
                        <div id="sidebarBoxCallerNumber" class="text-lg font-black text-white font-mono tracking-tight">
                            +1 (832) 390-8863
                        </div>
                        <div class="mt-2.5 pt-2 border-t border-slate-700/60 flex items-center justify-between">
                            <span class="text-[11px] text-slate-300 font-medium">🔔 Ringing Desktop App...</span>
                            <span class="text-[10px] font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-md">HD Voice</span>
                        </div>
                    </div>

                    <!-- Side-by-Side Large Circular Action Buttons -->
                    <div class="flex items-center justify-center gap-8 py-2">
                        <!-- Big Green Answer Button -->
                        <div class="flex flex-col items-center gap-2">
                            <button onclick="answerIncomingCall()" class="w-16 h-16 rounded-full bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-white flex items-center justify-center shadow-xl shadow-emerald-500/40 transition transform hover:scale-105 cursor-pointer animate-pulse" title="Answer Call">
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
                </div>'''

if target_ringing_controls in content:
    content = content.replace(target_ringing_controls, replacement_ringing_controls)
    print("Replaced incoming controls with sidebar Answering Box + Buttons!")
else:
    print("target_ringing_controls not found directly")

# 3. Update handleIncomingTwilioCall to set sidebarBoxCallerNumber
content = content.replace(
    '''            const banner = document.getElementById('incomingCallFloatingBanner');
            const bannerNum = document.getElementById('floatingBannerCallerNumber');
            if (bannerNum) bannerNum.textContent = formatted;
            if (banner) banner.classList.remove('hidden');''',
    '''            const boxNum = document.getElementById('sidebarBoxCallerNumber');
            if (boxNum) boxNum.textContent = formatted;'''
)

# 4. Clean up any hideIncomingCallFloatingBanner calls
content = content.replace('hideIncomingCallFloatingBanner();', '// floating banner removed from header')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("voice-app.html successfully updated: answering box moved from header to sidebar!")
