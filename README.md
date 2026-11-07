## Two Ways to Use Eigenlog

### Option 1: Expressing Your Mind in Python Code (For Developers & Tinkurers)
If you prefer expressing your thoughts and cognitive reflections programmatically in Python, import the `Mind` class:

```python
from eigenlog import Mind

# Initialize your running mind
m = Mind()

# Reflect on your internal state using the expanded world ontology
m.reflect(
    subject="emotions",
    observation="Feeling centered and focused after clearing old clutter",
    measure="8/10",
    doubt="Can I sustain this clarity tomorrow?"
)

# Read and inspect your cognitive log as a Pandas DataFrame
print(m.read())

# Check unresolved doubts or epistemic drift
print(m.open_doubts())
```

### Option 2: The Interactive CLI Practice (For Direct Reflection)
If you just want an interactive command prompt to log reflections on the fly without writing code each time:

```bash
python3 interactive_mind.py
```

## Features
- **Expanded World Ontology:** Covers body, brain, emotions (joy, fear, anger, sadness), spirit, love, grief, betrayal, culture, technology, and more.
- **100% Local & Private:** No cloud sync, no tracking, no AI telemetry—your thoughts stay strictly on your machine.
- **SQL & CSV Support:** Easily query your logs using pandas or SQL (`m.query("SELECT * FROM log WHERE subject = 'emotions'")`).

## Who is this for?
- **Technical users:** Run the Python, SQL, and Bash scripts to query your cognitive state, track epistemic drift, and manage your ontology.
- **Everyone else:** Ignore the code. Just open `log.csv` in Excel, Apple Numbers, or Google Sheets. Add your rows manually. The tool is ultimately just a structured text file. You don't need to write a single line of code to use it.

## Privacy & Data Sovereignty
> **WARNING: This tool logs highly sensitive, unfiltered personal data. Ensure your disk is fully encrypted (e.g., using LUKS on Linux, FileVault on macOS, or BitLocker on Windows). Your log files are created with strictly locked owner-only permissions (`0o600`). Keep them secure.**

This tool is ultimately private and unrecorded. There is no cloud, no login, no AI reading your entries, and no telemetry. Your reflections live exclusively on your local machine. In a world where your thoughts are treated as training data, Eigenlog is just a mirror. It doesn't phone home, because it doesn't have a phone.