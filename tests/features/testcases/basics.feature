Feature: Aeternum CLI initialization

    Scenario Outline: Verify base commands help
        Given I have the Aeternum CLI installed
        When I run "aeternum <command> --help"
        Then the CLI should return exit code 0
        Examples: Commands
            | command |
            | doctor  |
            | run     |
            | init    |

    Scenario: Running an invalid command
        Given I have the Aeternum CLI installed
        When I run "aeternum unknown_command"
        Then the stderr should contain "Error: No such command"
        And the CLI should return exit code 1
