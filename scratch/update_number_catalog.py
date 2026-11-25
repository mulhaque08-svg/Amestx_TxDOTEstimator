file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update availableNumberCatalog with DISTINCT new numbers (NO (844) 826-3789!)
old_catalog = '''        const availableNumberCatalog = {
            tollfree: [
                { number: "(844) 826-3789", label: "Toll-Free Nationwide (Primary Active Line)", id: "18448263789" },
                { number: "(844) 912-4420", label: "Toll-Free Nationwide (Commercial Dispatch)", id: "18449124420" },
                { number: "(888) 720-3901", label: "Toll-Free Nationwide (Estimator Bids)", id: "18887203901" }
            ],
            texas: [
                { number: "(210) 942-4238", label: "San Antonio / Bexar County Construction", id: "12109424238" },
                { number: "(512) 648-9102", label: "Austin / Central Texas Regional", id: "15126489102" },
                { number: "(713) 489-3321", label: "Houston Metro / Gulf Coast", id: "17134893321" },
                { number: "(832) 555-0199", label: "Houston South Commercial", id: "18325550199" },
                { number: "(214) 736-5540", label: "Dallas / Fort Worth North Texas", id: "12147365540" }
            ]
        };'''

new_catalog = '''        // Master Amestx line (844) 826-3789 is RESERVED for Admin and NEVER sold to other customers.
        // Catalog below contains brand-new, unique numbers available for new customers and additional lines.
        const availableNumberCatalog = {
            tollfree: [
                { number: "(844) 710-3320", label: "Toll-Free Nationwide — Commercial Line", id: "18447103320" },
                { number: "(855) 490-8812", label: "Toll-Free Nationwide — Dispatch & Bids", id: "18554908812" },
                { number: "(888) 630-1940", label: "Toll-Free Nationwide — Contractor Line", id: "18886301940" },
                { number: "(877) 512-7740", label: "Toll-Free Nationwide — Logistics Line", id: "18775127740" },
                { number: "(866) 389-9921", label: "Toll-Free Nationwide — Heavy Equipment", id: "18663899921" }
            ],
            texas: [
                { number: "(713) 489-3321", label: "Houston Metro — Central Texas", id: "17134893321" },
                { number: "(832) 410-6674", label: "Houston Metro — Commercial Line", id: "18324106674" },
                { number: "(281) 694-8830", label: "Houston / Gulf Coast — Industrial", id: "12816948830" },
                { number: "(210) 758-1194", label: "San Antonio / Bexar County Construction", id: "12107581194" },
                { number: "(512) 648-9102", label: "Austin / Central Texas Regional", id: "15126489102" },
                { number: "(512) 890-3415", label: "Austin Metro — Contractor Dispatch", id: "15128903415" },
                { number: "(214) 736-5540", label: "Dallas / Fort Worth — North Texas", id: "12147365540" },
                { number: "(817) 529-6810", label: "Fort Worth — Commercial Operations", id: "18175296810" },
                { number: "(361) 820-4155", label: "Corpus Christi — Coastal Bend", id: "13618204155" },
                { number: "(956) 410-7780", label: "McAllen / Rio Grande Valley", id: "19564107780" },
                { number: "(915) 308-6622", label: "El Paso — West Texas Borderplex", id: "19153086622" }
            ]
        };'''

if old_catalog in content:
    content = content.replace(old_catalog, new_catalog)
    print("Catalog updated with brand new distinct numbers!")
else:
    print("old_catalog exact string not found.")

# 2. Add Area Code search and reservation notice in the Modal
old_modal_content = '''                <!-- Area Code Selector Tabs -->
                <div>
                    <label class="text-xs font-bold text-slate-700 block mb-2">Select Number Region or Type:</label>
                    <div class="grid grid-cols-2 gap-2 text-xs font-bold">
                        <button onclick="filterNumbers('tollfree')" id="btnNumTollFree" class="py-2.5 px-3 rounded-xl border-2 border-blue-600 bg-blue-50 text-blue-700 flex items-center justify-center gap-1.5 transition">
                            <span>🇺🇸</span>
                            <span>Toll-Free Nationwide (844)</span>
                        </button>
                        <button onclick="filterNumbers('texas')" id="btnNumTexas" class="py-2.5 px-3 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-1.5 transition">
                            <span>⭐</span>
                            <span>Texas Local Lines</span>
                        </button>
                    </div>
                </div>

                <!-- Number Selection List -->
                <div>
                    <label class="text-xs font-bold text-slate-700 block mb-2">Available Phone Numbers Ready for Activation:</label>
                    <div class="space-y-2 max-h-48 overflow-y-auto custom-scrollbar pr-1" id="availableNumbersList">
                        <!-- Numbers rendered dynamically -->
                    </div>
                </div>'''

new_modal_content = '''                <!-- Reserved Admin Line Notice -->
                <div class="p-3 bg-blue-50/70 border border-blue-200/80 rounded-2xl flex items-center justify-between text-xs">
                    <div class="flex items-center gap-2">
                        <span class="text-base">🔒</span>
                        <div>
                            <span class="text-slate-600 font-medium">Your Master Business Line:</span>
                            <strong class="text-blue-900 font-mono font-bold block">(844) 826-3789</strong>
                        </div>
                    </div>
                    <span class="text-[10px] bg-blue-600 text-white font-extrabold px-2.5 py-0.5 rounded-full uppercase tracking-wider">Reserved &bull; Active</span>
                </div>

                <!-- Area Code Selector Tabs -->
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="text-xs font-bold text-slate-700">Choose New Dedicated Line:</label>
                        <span class="text-[11px] text-slate-500">Instant carrier activation</span>
                    </div>
                    <div class="grid grid-cols-2 gap-2 text-xs font-bold">
                        <button onclick="filterNumbers('tollfree')" id="btnNumTollFree" class="py-2.5 px-3 rounded-xl border-2 border-blue-600 bg-blue-50 text-blue-700 flex items-center justify-center gap-1.5 transition">
                            <span>🇺🇸</span>
                            <span>Toll-Free Nationwide (844/855/888)</span>
                        </button>
                        <button onclick="filterNumbers('texas')" id="btnNumTexas" class="py-2.5 px-3 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-1.5 transition">
                            <span>⭐</span>
                            <span>Texas Local Lines</span>
                        </button>
                    </div>
                </div>

                <!-- Live Area Code Search Filter -->
                <div class="relative">
                    <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs">🔍</span>
                    <input id="numSearchInput" oninput="handleNumberSearch(this.value)" type="text" placeholder="Search by area code or city (e.g. 713, 210, 512, 844, Dallas)..." class="w-full pl-9 pr-4 py-2.5 text-xs font-medium text-slate-800 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 focus:bg-white outline-none transition font-sans">
                </div>

                <!-- Number Selection List -->
                <div>
                    <div class="flex items-center justify-between mb-1.5">
                        <label class="text-xs font-bold text-slate-700">Available Numbers for Your Company:</label>
                        <span id="numberCountBadge" class="text-[10px] text-slate-500 font-semibold font-mono">5 available</span>
                    </div>
                    <div class="space-y-2 max-h-48 overflow-y-auto custom-scrollbar pr-1" id="availableNumbersList">
                        <!-- Numbers rendered dynamically -->
                    </div>
                </div>'''

if old_modal_content in content:
    content = content.replace(old_modal_content, new_modal_content)
    print("Modal content updated with search bar and master line notice!")
else:
    print("old_modal_content exact string not found.")

# 3. Add search filter function in JS
js_filter_functions = '''        function handleNumberSearch(query) {
            const list = document.getElementById('availableNumbersList');
            const badge = document.getElementById('numberCountBadge');
            if (!list) return;

            const q = (query || '').toLowerCase().trim();
            const allItems = [...(availableNumberCatalog.tollfree || []), ...(availableNumberCatalog.texas || [])];
            
            const filtered = q ? allItems.filter(item => 
                item.number.toLowerCase().includes(q) || 
                item.label.toLowerCase().includes(q) ||
                item.id.includes(q)
            ) : availableNumberCatalog[currentNumberCategory];

            if (badge) badge.textContent = `${filtered.length} available`;

            if (filtered.length === 0) {
                list.innerHTML = `
                    <div class="p-6 text-center text-slate-500 text-xs bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                        No numbers matched "${query}". Try searching <strong>844</strong>, <strong>713</strong>, <strong>210</strong>, or <strong>512</strong>.
                    </div>
                `;
                return;
            }

            renderNumberListItems(filtered);
        }

        function renderNumberListItems(items) {
            const list = document.getElementById('availableNumbersList');
            if (!list) return;

            list.innerHTML = items.map((item, idx) => `
                <label class="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-blue-400 hover:bg-blue-50/50 cursor-pointer transition">
                    <div class="flex items-center gap-3">
                        <input type="radio" name="selectedNumberRadio" value="${item.id}" data-num="${item.number}" data-label="${item.label}" ${idx === 0 ? 'checked' : ''} class="text-blue-600 mt-0.5">
                        <div>
                            <div class="text-xs font-black text-slate-900 font-mono tracking-tight">${item.number}</div>
                            <div class="text-[11px] text-slate-500">${item.label}</div>
                        </div>
                    </div>
                    <span class="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full flex-shrink-0">Available</span>
                </label>
            `).join('');
        }
'''

# Replace filterNumbers to use renderNumberListItems and update count badge
old_filter_func = '''            const items = availableNumberCatalog[category] || [];
            list.innerHTML = items.map((item, idx) => `
                <label class="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-blue-300 hover:bg-blue-50/40 cursor-pointer transition">
                    <div class="flex items-center gap-3">
                        <input type="radio" name="selectedNumberRadio" value="${item.id}" data-num="${item.number}" data-label="${item.label}" ${idx === 0 ? 'checked' : ''} class="text-blue-600">
                        <div>
                            <div class="text-xs font-black text-slate-900 font-mono">${item.number}</div>
                            <div class="text-[11px] text-slate-500">${item.label}</div>
                        </div>
                    </div>
                    <span class="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">Available</span>
                </label>
            `).join('');'''

new_filter_func = '''            const searchInp = document.getElementById('numSearchInput');
            if (searchInp) searchInp.value = '';

            const items = availableNumberCatalog[category] || [];
            const badge = document.getElementById('numberCountBadge');
            if (badge) badge.textContent = `${items.length} available`;

            renderNumberListItems(items);'''

if old_filter_func in content:
    content = content.replace(old_filter_func, new_filter_func)
    print("Updated filterNumbers function!")
else:
    print("old_filter_func exact string not found.")

# Insert js_filter_functions right above filterNumbers
if 'function renderNumberListItems' not in content:
    content = content.replace('function filterNumbers(category) {', js_filter_functions + '\n        function filterNumbers(category) {')
    print("Added search filter functions to JS!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("voice-app.html successfully updated with distinct numbers and search filter!")
