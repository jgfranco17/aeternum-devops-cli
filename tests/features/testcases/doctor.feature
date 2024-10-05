Feature: Aeternum CLI Doctor

    Background:
        Given I have the Aeternum CLI installed

    Scenario: Running the default doctor command
        When I run "aeternum doctor"
        Then the CLI should return exit code 0
        But the stdout should contain "Cannot build project without configuration file"

    Scenario: Running the doctor command with file argument
        Given I create the file "my_spec.yaml" in the current directory
        When I run "aeternum doctor -f my_spec.yaml"
        Then the CLI should return exit code 0
