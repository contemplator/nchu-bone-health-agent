import struct
import math
import csv

def ibm_to_ieee(b):
    """Convert 8-byte IBM 360 floating point to Python float (IEEE 754)."""
    if len(b) < 8:
        return None
    # SAS missing value: first byte is 0x2e ('.') or 0x5f ('_') or A-Z, followed by zeros
    if b[1:] == b'\x00\x00\x00\x00\x00\x00\x00' and b[0] != 0:
        return None
    if b == b'\x00\x00\x00\x00\x00\x00\x00\x00':
        return 0.0
    uint64 = struct.unpack('>Q', b)[0]
    sign = -1.0 if (uint64 >> 63) & 1 else 1.0
    exponent = ((uint64 >> 56) & 0x7f) - 64
    mantissa = uint64 & 0x00ffffffffffffff
    if mantissa == 0:
        return 0.0
    val = sign * (mantissa / float(1 << 56)) * (16.0 ** exponent)
    return val

def read_xpt(filepath):
    """Pure Python SAS XPORT (.xpt) v5 reader."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    namestr_marker = b'HEADER RECORD*******NAMESTR HEADER RECORD!!!!!!!'
    obs_marker = b'HEADER RECORD*******OBS     HEADER RECORD!!!!!!!'
    
    idx_namestr = data.find(namestr_marker)
    if idx_namestr == -1:
        raise ValueError(f"NAMESTR header not found in {filepath}")
    
    header_rec = data[idx_namestr:idx_namestr+80]
    num_vars = int(header_rec[54:58].decode('ascii').strip())
    
    pos = idx_namestr + 80
    vars_info = []
    cum_pos = 0
    for i in range(num_vars):
        rec = data[pos:pos+140]
        ntype, nhfun, nlng, nvar0 = struct.unpack('>hhhh', rec[0:8])
        nname = rec[8:16].decode('ascii', errors='ignore').strip()
        nlabel = rec[16:56].decode('ascii', errors='ignore').strip()
        vars_info.append({
            'name': nname,
            'label': nlabel,
            'type': ntype, # 1 = numeric, 2 = char
            'length': nlng,
            'pos': cum_pos
        })
        cum_pos += nlng
        pos += 140
    
    idx_obs = data.find(obs_marker, pos)
    obs_start = idx_obs + 80
    row_len = cum_pos
    
    rows = []
    cur = obs_start
    total_len = len(data)
    while cur + row_len <= total_len:
        row_bytes = data[cur:cur+row_len]
        if row_bytes == b' ' * row_len:
            break
        row = {}
        for v in vars_info:
            field_bytes = row_bytes[v['pos']:v['pos']+v['length']]
            if v['type'] == 1:
                row[v['name']] = ibm_to_ieee(field_bytes)
            else:
                row[v['name']] = field_bytes.decode('ascii', errors='ignore').strip()
        rows.append(row)
        cur += row_len
    return vars_info, rows

base_dir = "/Users/leolin/Documents/NCHU_Programs/nchu-bone-health-agent/data/raw"
processed_dir = "/Users/leolin/Documents/NCHU_Programs/nchu-bone-health-agent/data/processed"

print("Reading XPT files using pure Python parser...")
fem_vars, fem_rows = read_xpt(f"{base_dir}/P_DXXFEM.xpt")
demo_vars, demo_rows = read_xpt(f"{base_dir}/P_DEMO.xpt")
bmx_vars, bmx_rows = read_xpt(f"{base_dir}/P_BMX.xpt")
osq_vars, osq_rows = read_xpt(f"{base_dir}/P_OSQ.xpt")

print(f"\n=== 1. Raw Dataset Record Counts ===")
print(f"P_DXXFEM (股骨 DXA): {len(fem_rows)} rows, {len(fem_vars)} columns")
print(f"P_DEMO   (人口學):   {len(demo_rows)} rows, {len(demo_vars)} columns")
print(f"P_BMX    (身體測量): {len(bmx_rows)} rows, {len(bmx_vars)} columns")
print(f"P_OSQ    (骨鬆問卷): {len(osq_rows)} rows, {len(osq_vars)} columns")

# Index DEMO, BMX, OSQ by int(SEQN)
demo_dict = {int(round(r['SEQN'])): r for r in demo_rows if r.get('SEQN') is not None}
bmx_dict  = {int(round(r['SEQN'])): r for r in bmx_rows  if r.get('SEQN') is not None}
osq_dict  = {int(round(r['SEQN'])): r for r in osq_rows  if r.get('SEQN') is not None}

valid_records = []
for r in fem_rows:
    if r.get('SEQN') is None:
        continue
    seqn = int(round(r['SEQN']))
    nkbmd = r.get('DXXNKBMD')
    ofbmd = r.get('DXXOFBMD')
    if nkbmd is None or ofbmd is None:
        continue
    
    demo = demo_dict.get(seqn, {})
    bmx = bmx_dict.get(seqn, {})
    osq = osq_dict.get(seqn, {})
    
    # Calculate WHO T-scores (NHANES III 20-29 Non-Hispanic White Female Reference)
    # Femoral Neck: Mean = 0.858, SD = 0.120
    # Total Femur:  Mean = 0.942, SD = 0.122
    t_neck = (nkbmd - 0.858) / 0.120
    t_total = (ofbmd - 0.942) / 0.122
    min_t = min(t_neck, t_total)
    
    if min_t >= -1.0:
        who_cat = "Normal (正常)"
    elif min_t > -2.5:
        who_cat = "Osteopenia (骨量減少)"
    else:
        who_cat = "Osteoporosis (骨質疏鬆)"
        
    gender_code = demo.get('RIAGENDR')
    gender_str = "男 (Male)" if gender_code == 1.0 else ("女 (Female)" if gender_code == 2.0 else "Unknown")
    age = int(round(demo['RIDAGEYR'])) if demo.get('RIDAGEYR') is not None else None
    bmi = round(bmx['BMXBMI'], 1) if bmx.get('BMXBMI') is not None else None
    wt  = round(bmx['BMXWT'], 1) if bmx.get('BMXWT') is not None else None
    ht  = round(bmx['BMXHT'], 1) if bmx.get('BMXHT') is not None else None
    
    # OSQ060: Ever told had osteoporosis/brittle bones (1=Yes, 2=No)
    osq060 = osq.get('OSQ060')
    told_osteo = "Yes (曾確診)" if osq060 == 1.0 else ("No (未曾)" if osq060 == 2.0 else "N/A")
    # OSQ010A: Broken or fractured a hip (1=Yes, 2=No)
    osq010a = osq.get('OSQ010A')
    hip_fx = "Yes (曾髖部骨折)" if osq010a == 1.0 else ("No (無)" if osq010a == 2.0 else "N/A")

    rec = {
        'SEQN': seqn,
        'Gender': gender_str,
        'Age': age,
        'Weight_kg': wt,
        'Height_cm': ht,
        'BMI': bmi,
        'Total_Femur_BMD': round(ofbmd, 4),
        'Total_Femur_BMC': round(r['DXXOFBMC'], 2) if r.get('DXXOFBMC') else None,
        'Total_Femur_Area': round(r['DXXOFA'], 2) if r.get('DXXOFA') else None,
        'Femoral_Neck_BMD': round(nkbmd, 4),
        'Femoral_Neck_BMC': round(r['DXXNKBMC'], 2) if r.get('DXXNKBMC') else None,
        'Femoral_Neck_Area': round(r['DXXNKA'], 2) if r.get('DXXNKA') else None,
        'Trochanter_BMD': round(r['DXXTRBMD'], 4) if r.get('DXXTRBMD') else None,
        'Intertrochanter_BMD': round(r['DXXINBMD'], 4) if r.get('DXXINBMD') else None,
        'T_score_Total_Femur': round(t_total, 2),
        'T_score_Femoral_Neck': round(t_neck, 2),
        'Min_T_score': round(min_t, 2),
        'WHO_Category': who_cat,
        'Doctor_Told_Osteoporosis': told_osteo,
        'History_Hip_Fracture': hip_fx
    }
    valid_records.append(rec)

print(f"\n=== 3. Valid DXA Scans Count ===")
print(f"Total rows in P_DXXFEM: {len(fem_rows)}")
print(f"Valid completed DXA scans (non-null BMD): {len(valid_records)}")

# Distribution
counts = {}
for rec in valid_records:
    c = rec['WHO_Category']
    counts[c] = counts.get(c, 0) + 1

print(f"\n=== 4. WHO Diagnostic Distribution Across All {len(valid_records)} Subjects ===")
for k, v in counts.items():
    print(f"  - {k:22s}: {v:4d} 人 ({v/len(valid_records)*100:.2f}%)")

# Pick 5 concrete examples to show step-by-step calculation
ex_normal = next(r for r in valid_records if r['WHO_Category'] == "Normal (正常)" and r['Age'] >= 55)
ex_osteopenia = next(r for r in valid_records if r['WHO_Category'] == "Osteopenia (骨量減少)" and r['Age'] >= 65)
ex_osteoporosis = next(r for r in valid_records if r['WHO_Category'] == "Osteoporosis (骨質疏鬆)" and r['Doctor_Told_Osteoporosis'] == "No (未曾)")
ex_confirmed = next(r for r in valid_records if r['WHO_Category'] == "Osteoporosis (骨質疏鬆)" and r['Doctor_Told_Osteoporosis'] == "Yes (曾確診)")
ex_fracture = next(r for r in valid_records if r['History_Hip_Fracture'] == "Yes (曾髖部骨折)")

examples = [
    ("個案 1：骨骼健康長者 (Normal)", ex_normal),
    ("個案 2：骨量減少預警 (Osteopenia)", ex_osteopenia),
    ("個案 3：潛在未確診之骨質疏鬆患者 (Silent Osteoporosis)", ex_osteoporosis),
    ("個案 4：臨床已確診之重度骨質疏鬆患者 (Confirmed Osteoporosis)", ex_confirmed),
    ("個案 5：曾發生髖部骨折之高危患者 (Hip Fracture Case)", ex_fracture)
]

print("\n=== 5. Real Patient Examples & T-score Verification ===")
for title, ex in examples:
    print(f"\n--- {title} ---")
    for k, v in ex.items():
        print(f"  {k:25s}: {v}")

# Save processed CSV
csv_path = f"{processed_dir}/nhanes_dxa_femur_merged_with_tscore.csv"
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(valid_records[0].keys()))
    writer.writeheader()
    writer.writerows(valid_records)
print(f"\nSaved all {len(valid_records)} merged & calculated records to: {csv_path}")
