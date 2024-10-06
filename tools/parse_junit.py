import os
import xml.etree.ElementTree as ET


def parse_junit_xml(junit_file: str) -> dict:
    """Parses a single JUnit XML file and returns test cases info."""
    tree = ET.parse(junit_file)
    root = tree.getroot()

    test_cases = []
    for testcase in root.iter("testcase"):
        name = testcase.attrib["name"]
        classname = testcase.attrib["classname"]
        time = testcase.attrib["time"]
        status = "PASSED"

        # Check for failures or errors
        failure = testcase.find("failure")
        error = testcase.find("error")
        if failure is not None:
            status = f"FAILED: {failure.attrib.get('message', 'No message')}"
        elif error is not None:
            status = f"ERROR: {error.attrib.get('message', 'No message')}"

        test_cases.append(
            {"name": name, "classname": classname, "time": time, "status": status}
        )

    # Gather summary stats
    total_tests = len(root.findall(".//testcase"))
    failed_tests = len(root.findall(".//failure"))
    error_tests = len(root.findall(".//error"))

    return {
        "test_cases": test_cases,
        "total_tests": total_tests,
        "failed_tests": failed_tests,
        "error_tests": error_tests,
    }


def junit_reports_to_markdown(junit_dir: str, output_file: str) -> None:
    """Converts multiple JUnit XML reports to a single Markdown file."""
    markdown_content = ""
    total_tests = 0
    total_failures = 0
    total_errors = 0

    for filename in os.listdir(junit_dir):
        if filename.endswith(".xml"):
            junit_file = os.path.join(junit_dir, filename)
            test_results = parse_junit_xml(junit_file)

            markdown_content += f"## Results from {filename}\n\n"
            for testcase in test_results["test_cases"]:
                markdown_content += (
                    f"### {testcase['name']} ({testcase['classname']})\n\n"
                )
                markdown_content += f"**Status**: {testcase['status']}\n\n"
                markdown_content += f"**Time**: {testcase['time']} seconds\n\n"
                markdown_content += "---\n\n"

            # Aggregate the results
            total_tests += test_results["total_tests"]
            total_failures += test_results["failed_tests"]
            total_errors += test_results["error_tests"]

    # Write summary
    markdown_content += "## Summary\n\n"
    markdown_content += f"**Total Tests**: {total_tests}\n\n"
    markdown_content += f"**Failed**: {total_failures}\n\n"
    markdown_content += f"**Errors**: {total_errors}\n\n"

    # Write to the markdown file
    with open(output_file, "w") as md_file:
        md_file.write(markdown_content)


if __name__ == "__main__":
    junit_reports_to_markdown("reports", "behave_report.md")
