Feature: Aeternum CLI initialization

    Background:
        Given I have the Aeternum CLI installed

    Scenario: Running the default doctor command
        When I run "aeternum doctor"
        Then the CLI should return exit code 0

    Scenario: Running the doctor command with file argument
        Given I create the file "my_spec.yaml" in the current directory
        When I run "aeternum doctor -f my_spec.yaml"
        Then the CLI should return exit code 0

    Scenario: Running an invalid command
        When I run "aeternum unknown_command"
        Then the stderr should contain "Error: No such command"
        And the CLI should return exit code 1
