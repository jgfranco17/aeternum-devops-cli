import os
import re
from xml.etree import ElementTree as ET


def extract_coverage_from_xml(file_path: str) -> float:
    """Extracts the total coverage percentage from a coverage.xml file."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    coverage = root.attrib.get("line-rate")
    return float(coverage) * 100  # Convert to percentage


def update_readme(readme_path: str, coverage: float):
    """Updates the README.md file with the new coverage value."""
    with open(readme_path, "r") as f:
        content = f.read()

    new_content = re.sub(r"(?<=Coverage: )\d+\.?\d*%", f"{coverage:.2f}%", content)

    with open(readme_path, "w") as f:
        f.write(new_content)


if __name__ == "__main__":
    coverage_file = "coverage.xml"
    readme_file = "README.md"

    if not os.path.exists(coverage_file):
        raise FileNotFoundError(
            f"{coverage_file} not found. Did the coverage report generate correctly?"
        )

    coverage_percentage = extract_coverage_from_xml(coverage_file)
    print(f"Extracted coverage: {coverage_percentage:.2f}%")

    update_readme(readme_file, coverage_percentage)
    print(f"Updated {readme_file} with the new coverage value.")
