file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        function initApp() {'''

replacement = '''        function loadSavedPaidLines() {
            try {
                const saved = JSON.parse(localStorage.getItem('amestx_paid_lines') || '[]');
                const select = document.getElementById('callerIdSelect');
                if (!select) return;

                saved.forEach(item => {
                    if (typeof paidLinesRegistry !== 'undefined' && !paidLinesRegistry.includes(item.id)) {
                        paidLinesRegistry.push(item.id);
                    }
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
                        opt.textContent = `★ ${item.number} (${item.label ? item.label.split(' ')[0] : 'Active'} • Dedicated Line)`;
                        if (select.options.length > 0) {
                            select.insertBefore(opt, select.options[select.options.length - 1]);
                        } else {
                            select.appendChild(opt);
                        }
                    }
                });
            } catch (err) {
                console.warn("Could not load saved lines:", err);
            }
        }

        function initApp() {'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully added loadSavedPaidLines definition!")
else:
    print("target not found")
