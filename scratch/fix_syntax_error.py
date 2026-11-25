file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

broken_func = '''        function formatPhoneNumber(raw) {
            const digits = (raw || '').replace(/\\D/g, '');
            if (digits.length === 10) {
                return () -;
            } else if (digits.length === 11 && digits.startsWith('1')) {
                return +1 () -;
            }
            return raw;
        }'''

fixed_func = '''        function formatPhoneNumber(raw) {
            if (!raw) return '';
            const digits = ('' + raw).replace(/\\D/g, '');
            if (digits.length === 10) {
                return '(' + digits.slice(0, 3) + ') ' + digits.slice(3, 6) + '-' + digits.slice(6);
            } else if (digits.length === 11 && digits.charAt(0) === '1') {
                return '+1 (' + digits.slice(1, 4) + ') ' + digits.slice(4, 7) + '-' + digits.slice(7);
            }
            return raw;
        }'''

if broken_func in content:
    content = content.replace(broken_func, fixed_func)
    print("Fixed formatPhoneNumber syntax error!")
else:
    # Try finding lines 994-1002 directly
    import re
    content = re.sub(
        r'function formatPhoneNumber\(raw\)\s*\{[^}]*\}',
        fixed_func.strip(),
        content
    )
    print("Replaced formatPhoneNumber via regex!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("voice-app.html updated successfully!")
