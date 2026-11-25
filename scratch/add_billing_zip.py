file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="text-xs font-bold text-slate-700 block mb-1">Expires (MM/YY)</label>
                            <input id="cardExpiry" type="text" required maxlength="5" placeholder="MM/YY" value="08/29" class="w-full px-3.5 py-2.5 text-xs font-mono font-bold text-slate-900 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition text-center">
                        </div>
                        <div>
                            <label class="text-xs font-bold text-slate-700 block mb-1">CVC Code</label>
                            <input id="cardCvc" type="password" required maxlength="4" placeholder="CVC" value="382" class="w-full px-3.5 py-2.5 text-xs font-mono font-bold text-slate-900 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition text-center">
                        </div>
                    </div>'''

replacement = '''                    <div class="grid grid-cols-3 gap-2.5">
                        <div>
                            <label class="text-xs font-bold text-slate-700 block mb-1">Expires (MM/YY)</label>
                            <input id="cardExpiry" type="text" required maxlength="5" placeholder="MM/YY" value="08/29" class="w-full px-2.5 py-2.5 text-xs font-mono font-bold text-slate-900 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition text-center">
                        </div>
                        <div>
                            <label class="text-xs font-bold text-slate-700 block mb-1">CVC Code</label>
                            <input id="cardCvc" type="password" required maxlength="4" placeholder="CVC" value="382" class="w-full px-2.5 py-2.5 text-xs font-mono font-bold text-slate-900 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition text-center">
                        </div>
                        <div>
                            <label class="text-xs font-bold text-slate-700 block mb-1">Billing ZIP</label>
                            <input id="cardBillingZip" type="text" required maxlength="5" placeholder="ZIP" value="78205" class="w-full px-2.5 py-2.5 text-xs font-mono font-bold text-slate-900 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition text-center">
                        </div>
                    </div>'''

if target in text:
    text = text.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated checkout grid with Billing ZIP successfully!')
else:
    print('Target not found')
