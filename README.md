# AT Baseline Verifier – Python Backend

This is the backend automation engine for the **AT Baseline Verifier** project.  
It processes baseline test data, validates it, and generates reports consumed by the WPF (C#) frontend.

---

## 🎯 Purpose
- Validate baseline test cases against defined standards.  
- Process large datasets quickly and consistently.  
- Export results as structured logs and HTML reports.  
- Provide reliable data for the WPF UI to visualize.  

---

## ⚙️ How It Works
1. The WPF app sends user input or config to the Python engine.  
2. Python scripts process the input (CSV, Excel, or database queries).  
3. Validation results are generated as:  
   - Structured log files (`automation_log.txt`)  
   - Rich HTML reports  
4. WPF consumes these outputs and displays them in the Solo Leveling–inspired UI.  

---

## ▶️ Running the Python Module
From the project root:

```bash
   python main.py --input data/test_cases.csv --output results/report.html
