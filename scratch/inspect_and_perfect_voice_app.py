import os, re

file_path = r'C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\voice-app.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("File length:", len(content))

# 1. Inspect callerIdSelect
caller_m = re.search(r'<select id="callerIdSelect"[\s\S]*?</select>', content)
if caller_m:
    print("Found callerIdSelect:\n", caller_m.group(0))

# 2. Inspect modal
modal_m = re.search(r'<div id="purchaseNumberModal"[\s\S]*?<!-- End purchaseNumberModal -->', content)
if not modal_m:
    modal_m = re.search(r'<div id="purchaseNumberModal"[\s\S]*?</form>\s*</div>\s*</div>\s*</div>', content)
if modal_m:
    print("Found modal:\n", modal_m.group(0)[:500], "...\n", modal_m.group(0)[-500:])

# 3. Inspect initTwilioVoice
print("initTwilioVoice in content:", 'initTwilioVoice' in content)
print("initTwilioVoice calls:", len(re.findall(r'initTwilioVoice\(', content)))

# 4. Check DOMContentLoaded
print("DOMContentLoaded listeners:", len(re.findall(r'DOMContentLoaded', content)))
