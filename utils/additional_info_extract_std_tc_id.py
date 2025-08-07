import re
from collections import OrderedDict

def extract_std_groups_from_additional_info(text):
    """
    Handles multi-line headers: e.g. 'Additional Tests Cycle 6 STD' + '\nID:'
    Groups by any block where any header line or its immediate next ends with ':' and header contains 'STD' or 'ID'.
    """
    groups = OrderedDict()
    lines = [ln.strip() for ln in text.splitlines()]
    i = 0
    while i < len(lines):
        line = lines[i]
        # Try to detect the start of a header: must mention STD or ID, anywhere (case-insensitive), even without colon
        if re.search(r'\b(std|id)\b', line, re.I):
            # Look ahead: if next non-empty line ends with ":", it's part of the header!
            header = line
            j = i + 1
            while j < len(lines) and lines[j] == '':
                j += 1
            if j < len(lines) and lines[j].endswith(":"):
                header = f"{header} {lines[j]}"
                i = j  # Move i to end of header
            elif line.endswith(":"):
                header = line
            # Now, collect lines after header as IDs, until next blank or end
            ids = []
            i += 1
            while i < len(lines) and lines[i]:
                # Ranges
                for start, end in re.findall(r'(\d+)\s*[-–]\s*(\d+)', lines[i]):
                    ids.extend(map(str, range(int(start), int(end)+1)))
                # Hashtags, TC, and plain nums
                ids += re.findall(r'#?T?C?(\d{3,6})\b', lines[i])
                i += 1
            unique_ids = sorted(set(ids), key=ids.index)
            if unique_ids:
                groups[header.strip()] = unique_ids
        else:
            i += 1
    return groups
# =============== TEST IT ✅ ===================
test_text = """
Configuration (Catheters/WS/ULS/PIU): No
How do the following states could impact defect’s severity (Delete or Fill in)
Ablation: No
Pacing: No
Regression: Yes, Regression from Previous version V8 Ph2 LMR
Data loss: No
Review: Not Relevant
Backup/Restore: Not Relevant 
  
  
  
Additional Tests Cycle 3 STD: 
#432 

Additional Tests Cycle 4 STD
1370, 357, 1337, 1372, 1373, 1375, 1376, 1378, 1379, 1399, 1424, 979 

Additional Tests Cycle 4:
ID: 1111 

Feather - Unique Functionality STD TC ID: 
780 + 781 
  
  
Additional Tests Cycle 6 STD  
ID: 1569-1570 

Feather - Unique Functionality STD TC ID: 
345 
"""

if __name__ == "__main__":
    groups = extract_std_groups_from_additional_info(test_text)
    for header, ids in groups.items():
        print(f"{header} -> {ids}")
