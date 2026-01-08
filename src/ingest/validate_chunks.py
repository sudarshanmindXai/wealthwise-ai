import json
import glob
import os

REQUIRED_FIELDS = {
    "doc_id",
    "doc_type",
    "text"
}

def validate_chunks(base_dir="data/knowledge"):
    errors = []
    files = glob.glob(os.path.join(base_dir, "**/*.jsonl"), recursive=True)

    if not files:
        print("❌ No JSONL files found under", base_dir)
        return

    print(f"🔍 Found {len(files)} JSONL files. Validating...")

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    errors.append((file_path, line_no, "Invalid JSON"))
                    continue

                missing = REQUIRED_FIELDS - obj.keys()
                if missing:
                    errors.append(
                        (file_path, line_no, f"Missing fields: {missing}")
                    )

    if errors:
        print("❌ VALIDATION FAILED")
        for e in errors[:10]:
            print(e)
        print(f"... {len(errors)} total errors")
    else:
        print("✅ VALIDATION PASSED — all JSONL files are clean")

if __name__ == "__main__":
    validate_chunks()