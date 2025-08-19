import re


def extract_tc_ids_from_additional_info(std_name: str, additional_info_text: str) -> list[int]:
    """
    Extract test case IDs for a given std_name from additional_info_text.
    Handles fuzzy matching and multiple separators.
    """
    lines = additional_info_text.splitlines()
    std_name_norm = re.sub(r"[\s\-]", "", std_name.lower())  # normalize
    tc_ids = []

    capture = False
    for line in lines:
        line_norm = re.sub(r"[\s\-]", "", line.lower())
        if std_name_norm in line_norm:
            capture = True
            continue

        if capture:
            # stop if we reach another STD name or header
            if "std" in line_norm:
                break

            # extract numbers separated by +, -, or ,
            numbers = re.findall(r"\b\d+\b", line)
            # tc_ids.extend(int(n) for n in numbers if n.isdigit())
            tc_ids.extend(n for n in numbers if n.isdigit())

            # stop if IDs line ends (optional: can capture multiple lines if needed)
            if numbers:
                break

    return tc_ids

# if __name__ == "__main__":
#     additional_info_text = """
#         Some other info
#     Additional Tests Cycle 1:
#     STD-Alpha
#     ID: 42 + 63 + 74
#     More text here
#     Additional Tests Cycle 2
#     Beta STD
#     12-34-56
#
#     Additional Tests Cycle 6 STD
#     #25 + #47 + #84
#
#     Some other info
#     Additional Tests Cycle 1:
#     STD-Alpha
#     ID: 42 + 63 + 74
#     More text here
#     Additional Tests Cycle 2
#     Beta STD
#     12-34-56
#     """
#
#     std_name = "Additional Tests Cycle 6 STD"
#
#     from pprint import pprint
#
#     tc_ids = extract_tc_ids_from_additional_info(std_name, additional_info_text)
#     print(f"Test case IDs for {std_name}':")
#     pprint(tc_ids)
