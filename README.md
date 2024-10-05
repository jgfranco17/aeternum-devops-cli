# Aeternum

Aeternum is a powerful, user-friendly Command-Line Interface (CLI) tool tailored for CI/CD
pipelines and build management. Designed to simplify the orchestration of complex build
processes, Aeternum offers a structured and reliable alternative to traditional scripting.
By leveraging project specifications defined in YAML files, this tool empowers developers
to streamline repetitive tasks and enhance automation across various environments.

Whether you're running a local build or deploying to production, Aeternum makes it easier
to achieve consistency, traceability, and scalability in your workflows.

In future iterations, a companion REST API will be available and integrated into this tool.

## Project Code Coverage

![Coverage](https://img.shields.io/badge/coverage-96.28-green?style=for-the-badge)

See latest coverage report in GHA summaries: [coverage workflow](https://github.com/jgfranco17/aeternum-devops-cli/actions/workflows/testing.yaml)

## About

### Why Use Aeternum?

While custom shell scripts have long been the go-to solution for automating build and
deployment processes, they come with limitations—such as lack of standardization, poor
maintainability, and a steep learning curve for new team members. Aeternum offers a more
structured and modern approach to CI/CD and build automation, addressing the pitfalls of
conventional scripting. Here's why:

#### Declarative Approach

Unlike traditional shell scripts, which are often imperative and error-prone, Aeternum adopts
a declarative approach. By using YAML files, you describe what needs to be done, and the tool
handles how to do it. This makes your build process easier to read, share, and maintain.

#### Built-in Validation

One of the biggest issues with shell scripts is the lack of structure, making validation and
error-checking difficult. Aeternum leverages Pydantic models for strict validation of your
project configuration, ensuring errors are caught early and handled gracefully.

#### Modularity and Reusability

Scripts tend to grow organically, becoming difficult to refactor or reuse. Aeternum provides a
modular way of defining build steps and strategies, allowing teams to easily compose reusable
automation blocks across different projects and environments.

#### Cross-platform Compatibility

Aeternum supports multiple shells, making it inherently cross-platform. No more worrying about
Bash versus PowerShell incompatibilities: Aeternum allows developers to run builds on Windows,
Linux, and macOS environments with minimal friction.

#### CI/CD Integration

Aeternum is built to integrate seamlessly into CI/CD systems like GitHub Actions, GitLab CI,
Jenkins, and more. Whether you're building or deploying, you can plug Aeternum into your
pipeline to provide consistent, repeatable, and validated workflows.

### Key Features

**Spec-driven Automation:** Aeternum uses project specification files (in YAML format), which
define build steps and deployment strategies. Each step can be independently defined, ordered,
and customized, making the tool highly flexible for complex builds.

**Pydantic-powered Validation:** With Pydantic models at its core, Aeternum ensures that the
project specification files are well-formed and validated before any build or deployment starts.
This reduces human errors and minimizes unexpected behavior due to malformed configurations.

**Shell-agnostic Build Steps**: Developers can specify different shell environments (like Bash,
Zsh, or even PowerShell) for individual build steps, allowing cross-platform compatibility and
flexibility.

**Click-based CLI:** The intuitive, Click-based command structure makes the tool easy to learn
and use, even for those new to Python or CI/CD scripting. Command output and error handling
are clearly defined, enhancing the user experience.

**Execution Feedback:** The tool comes with an integrated progress bar that tracks and displays
the build steps dynamically, providing real-time feedback. Logs for each step are printed
underneath and can even be exported, making it easy to monitor long-running operations.

## Development Setup

### Preqrequisites

Before getting started on development for this project, install the following on your local machine:

- [Python 3.10](https://www.python.org/downloads/) or above

Additional installs; optional, for developer convenience

- [Just](https://github.com/casey/just) command runner
- [Direnv](https://direnv.net/docs/installation.html)

Aeternum can be installed using Poetry. Ensure you have Poetry installed on your system.

1. Clone the repository

   ```shell
   git clone https://github.com/jgfranco17/aeternum-devops-cli.git
   cd aeternum-devops-cli
   ```

2. Install dependencies

   ```shell
   poetry install
   ```

3. Use a virtual environment for development

   ```shell
   poetry shell
   poetry run aeternum --version
   ```

There is also a Docker implementation available.

```shell
docker build -t aeternum:latest .
docker run --rm aeternum:latest --version
```

## Quick-Start Guide

### Step 1: Define your project specification

Create a YAML configuration file (e.g., `project_spec.yaml`) that outlines the build steps for your project.
If no file name is passed, the default configuration file that Aeternum will search for is a `aeternum.yaml`
file at the current directory.

```yaml
# aeternum.yaml
name: "test-project"
repo-url: "https://github.com/some-user/my-test-project"
version: "0.1.0"
build-stage:
  strategy:
    strict: true

  steps:
    - name: "List dependencies"
      shell: "/bin/bash"
      type: "build"
      command: "pip"
      args: ["install", "-r", "requirements.txt"]

    - name: "Run test suite"
      shell: "/bin/zsh"
      type: "test"
      command: "pytest"
      args: ["-vv"]

    - name: "Push changes"
      type: "deploy"
      command: "kubectl"
      args: ["--as", "prod-admin", "restart"]
      shell: "/bin/sh"
```

### Step 2: Run Aeternum CLI

Once your YAML spec is ready, you can execute the defined steps using the Aeternum CLI:

```bash
aeternum build -f ./scripts/basic.yaml
```

Aeternum will validate the spec, execute each step in the specified shell, and provide
real-time progress feedback with logs.

## Advanced Usage

### Customizing build steps

Aeternum allows you to customize each build step by specifying the shell, commands, and
arguments for each step.

### GitHub Actions Integration

Aeternum is designed to work smoothly in CI/CD environments. To integrate it with GitHub
Actions, add a job in your workflow YAML file:

```yaml
# .github/workflows/ci-cd.yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install dependencies
        run: pip install aeternum
      - name: Run Aeternum
        run: aeternum build -f project_spec.yaml
```

## Contributing

We welcome contributions to Aeternum! Whether you're fixing bugs, adding new features, or
improving the documentation, your efforts are appreciated.

### How to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/my-feature`).
5. Create a [pull request](https://github.com/jgfranco17/aeternum-devops-cli/pulls).

Make sure to include tests for any new functionality and to adhere to the code style
guidelines in this repository.
