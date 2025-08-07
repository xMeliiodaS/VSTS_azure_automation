import re

def extract_std_tc_ids_from_additional_info(text):
    """
    Extracts all STD TC IDs from free-text additional info.
    Handles common formats: numbers, plus, comma, dash/range, etc.
    Returns a list of unique string IDs.
    """

    # Lowercase and unify text for easier searching
    text = text.lower()
    id_candidates = set()

    # 1. Look for explicit "std tc id" or similar lines
    std_lines = re.findall(
        r'(std[\s\-]*(tc)?[\s\-]*id[\s\:\-\=]*[^\n]+)', text, flags=re.I)

    for line, _ in std_lines:
        # Find all numbers in the line
        numbers = re.findall(r'\d+', line)
        id_candidates.update(numbers)
        # Check for ranges like 1569-1570
        for range_match in re.findall(r'(\d+)\s*[-–]\s*(\d+)', line):
            id_candidates.update(map(str, range(int(range_match[0]), int(range_match[1]) + 1)))

    # 2. Look for any "id: ####", numbers connected by +, ,, or -
    other_matches = re.findall(r'\b(\d{3,5})(?:\s*[\+\-,]\s*|\b)', text)
    id_candidates.update(other_matches)

    # Remove empty strings and return sorted list as strings
    return sorted(list(filter(None, id_candidates)))

test_text = """
Configuration (Catheters/WS/ULS/PIU): No
How do the following states could impact defect’s severity (Delete or Fill in)
Ablation: No
Pacing: No
Regression: No, Not relevant to Previous version V8 P2 LMR
Data loss: No
Review: Not Relevant
Backup/Restore: Not Relevant 

Feather - Unique Functionality STD TC ID: 
780 + #781 

Additional Tests Cycle 6 STD  
ID: 1569-1570 

Additional Tests Cycle 6 STD  
1111, 2222, 3333 

****Shaper tracker is active. *** 

Why does this bug happen and what triggers it? 
Basically, the Feather Shape Tracker XML overrides the magnetic thresholds in the registry. As a result, the Magnetic Indication (horseshoe) display aligns with the thresholds defined in the Feather Shape Tracker XML, while the colors in the Metal Values window are based on the thresholds set in the registry. 

Example MetalSensorData values: 
 <MetalSensorData InfoMetalThresholdMM = "1.50" SubOptimalMetalThresholdMM="2.99" BadMetalThresholdMM="9.99" InfoMetalThresholdDeg = "9.99" SubOptimalMetalThresholdDeg="14.99" BadMetalThresholdDeg="19.99" />
"""


additional_std_ids = extract_std_tc_ids_from_additional_info(test_text)
print("STD IDs found in Additional Info:", additional_std_ids)

print(additional_std_ids)