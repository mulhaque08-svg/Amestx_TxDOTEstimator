import zlib
import struct
import math
import os

def create_png(width, height, draw_func, filename):
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0) # filter byte: None
        for x in range(width):
            r, g, b, a = draw_func(x, y, width, height)
            raw_data.extend([r, g, b, a])
            
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)) # 8-bit RGBA
    idat = chunk(b'IDAT', zlib.compress(bytes(raw_data), 9))
    iend = chunk(b'IEND', b'')
    
    with open(filename, 'wb') as f:
        f.write(header + ihdr + idat + iend)
    print(f"Generated {filename}")

def ios_amestx_icon(x, y, w, h):
    # Normalized coordinates from -1.0 to 1.0
    nx = (x / w) * 2.0 - 1.0
    ny = (y / h) * 2.0 - 1.0
    
    # 1. Background Gradient (Dark Navy to Midnight Blue) - Solid, NO transparency for iOS!
    # Apple automatically applies its own squircle mask to the square image.
    grad = (ny + 1.0) / 2.0
    bg_r = int(11 + grad * 15)  # #0b132b -> #1a2744
    bg_g = int(19 + grad * 20)
    bg_b = int(43 + grad * 25)
    
    # Subtle radial highlight in center-top
    rad_dist = math.sqrt(nx*nx + (ny + 0.3)**2)
    if rad_dist < 1.0:
        highlight = int((1.0 - rad_dist) * 35)
        bg_r = min(255, bg_r + highlight // 2)
        bg_g = min(255, bg_g + highlight)
        bg_b = min(255, bg_b + highlight * 2)

    # 2. Left Translation Bubble (Vibrant Cyan #00e5ff)
    # Circle at (-0.18, -0.05), radius 0.46
    d_cyan = math.sqrt((nx + 0.18)**2 + (ny + 0.05)**2)
    if d_cyan < 0.46:
        # Border glow
        if d_cyan > 0.41:
            return (0, 229, 255, 255) # Bright cyan
        # Inside cyan gradient
        c_val = (d_cyan / 0.41)
        r = int(0 * c_val)
        g = int(160 + (1.0 - c_val) * 60)
        b = int(220 + (1.0 - c_val) * 35)
        
        # Stylized voice soundwave dots inside cyan bubble
        if -0.15 < ny < 0.05:
            # 3 soundwave lines
            for bar_x in [-0.28, -0.18, -0.08]:
                if abs(nx - bar_x) < 0.022 and abs(ny + 0.05) < (0.12 if bar_x == -0.18 else 0.07):
                    return (255, 255, 255, 255)
        return (r, g, b, 255)

    # 3. Right Translation Bubble (Construction Gold/Amber #ffb703)
    # Circle at (0.24, 0.15), radius 0.40
    d_gold = math.sqrt((nx - 0.24)**2 + (ny - 0.15)**2)
    if d_gold < 0.40:
        if d_gold > 0.35:
            return (255, 183, 3, 255) # Bright gold
        g_val = (d_gold / 0.35)
        r = int(245 - g_val * 25)
        g = int(140 - g_val * 20)
        b = int(0)
        
        # Stylized soundwave lines inside gold bubble
        if 0.05 < ny < 0.25:
            for bar_x in [0.16, 0.24, 0.32]:
                if abs(nx - bar_x) < 0.020 and abs(ny - 0.15) < (0.10 if bar_x == 0.24 else 0.06):
                    return (255, 255, 255, 255)
        return (r, g, b, 255)

    # 4. Stylized "A" (Amestx) branding badge at bottom
    if 0.62 < ny < 0.78 and abs(nx) < 0.55:
        # Subtle glowing line below
        if abs(ny - 0.70) < 0.015:
            glow_x = 1.0 - abs(nx) / 0.55
            return (0, int(229 * glow_x), int(255 * glow_x), 255)

    return (bg_r, bg_g, bg_b, 255)

dirs = [
    r"C:\Users\fibrg\OneDrive\Documents\GitHub\Amestx_TxDOTEstimator\communicator",
    r"C:\Users\fibrg\.gemini\antigravity\scratch\TxDOT_Estimator_Web\communicator"
]

for d in dirs:
    if os.path.exists(d):
        create_png(180, 180, ios_amestx_icon, os.path.join(d, "apple-touch-icon.png"))
        create_png(192, 192, ios_amestx_icon, os.path.join(d, "icon-192.png"))
        create_png(512, 512, ios_amestx_icon, os.path.join(d, "icon-512.png"))
