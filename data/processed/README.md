# Processed Data

Processed CSV files are generated locally by `python main.py` and are intentionally excluded from Git.

GitHub repository README content can include third-party credential examples or webhook URLs. Keeping generated processed tables local prevents those untrusted strings from entering release history. The repository retains deterministic sample data under `data/sample/` and final presentation artifacts under `outputs/`.
