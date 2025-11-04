Feature: View incomplete tasks for a course
  As a student, I want to view incomplete tasks for a course so that I can plan my work accordingly.

  Background:
    Given the server is running
    And the following course todo lists exist for view tasks:
      | title    | completed | description            | active |
      | COMP 302 | false     | Programming Languages  | true   |
      | SOCI 222 | false     | Urban Sociology        | true   |
    And the following todos exist for view tasks:
      | title                 | doneStatus | description                       |
      | Write lab report      | false      | Section 3 needs revision          |
      | Prepare presentation  | false      | Slides due next Monday            |
      | Submit reading memo   | false      | Chapter 4 of Urban Sociology      |

  Scenario Outline: Query incomplete tasks for a course (Normal flow)
    Given the view tasks endpoint "/projects/<course_id>/tasks" is available
    When I send a view tasks POST request to "/projects/<course_id>/tasks" with JSON body:
      """
      { "id": "<todo_id>" }
      """
    When I send a view tasks GET request to "/projects/<course_id>/tasks?doneStatus=false"
    Then the view tasks response status code should be 200

    Examples:
      | course    | course_id | todo_id |
      | COMP 302  | 1         | 2       |

  Scenario Outline: Query incomplete tasks for a course with no tasks (Alternate flow)
    Given the view tasks endpoint "/projects/<course_id>/tasks" is available
    When I send a view tasks GET request to "/projects/<course_id>/tasks?doneStatus=false"
    Then the view tasks response status code should be 200
    And the view tasks response body should be an empty array

    Examples:
      | course   | course_id |
      | SOCI 222 | 2         |

  # EXPECTED: 404 Not Found when project does not exist
  # ACTUAL (BUG): API returns 200 with a list. Accept 200 here to document behavior.
  Scenario Outline: Query incomplete tasks from a non-existent course (Error flow - BUG)
    When I send a view tasks GET request to "/projects/<course_id>/tasks?doneStatus=false"
    Then the view tasks response status code should be 200

    Examples:
      | course_id |
      | 9999      |
