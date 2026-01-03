import json

REQUIRED_FIELDS = {
    "doc_id",
    "doc_type",
    "section",
    "sub_section",
    "ay",
    "text"
}

def validate_chunks(file_path: str):
    errors = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"Line {line_no}: Invalid JSON")
                continue

            missing = REQUIRED_FIELDS - obj.keys()
            if missing:
                errors.append(
                    f"Line {line_no}: Missing fields {missing}"
                )

    return errors


if __name__ == "__main__":
    path = "data_processed/chunks.jsonl"
    errs = validate_chunks(path)
    if errs:
        print("Validation FAILED:")
        for e in errs:
            print(e)
    else:
        print("Validation PASSED: chunks.jsonl looks good.")