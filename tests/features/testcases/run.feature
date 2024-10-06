Feature: Aeternum CLI Run

    Background:
        Given I have the Aeternum CLI installed

    Scenario Outline: Executing the run command in dry-run mode
        Given I have reference file "<file>" captured as "spec_file"
        When I run "aeternum run -f $[spec_file] --dry-run"
        Then the CLI should return exit code 0
        Examples: Commands
            | file                 |
            | valid/aeternum.yaml  |
            | valid/minimal.yaml   |
