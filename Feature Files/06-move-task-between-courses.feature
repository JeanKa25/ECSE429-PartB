Feature: Move a task between course lists

  As a student, I want to move a task from one course list to another so that my tasks stay organized by the correct course.

  Background:
    Given the server is running
    And the following course todo lists exist:
      | title     | completed | description            | active |
      | COMP 302  | false     | Programming Languages  | true   |
      | SOCI 222  | false     | Urban Sociology        | true   |
    And the following todos exist:
      | title                 | doneStatus | description                    |
      | Prepare presentation  | false      | Slides due next Thursday       |
      | Submit reading memo   | false      | Chapter 4 summary              |
    And the todo "Prepare presentation" is linked to the course "COMP 302"

  Scenario Outline: Move a task from one existing course to another (Normal flow)
    Given I resolve the course id for "<from_course>" as "<from_id>"
    And I resolve the todo id for "<todo_title>" as "<todo_id>"
    When I send a DELETE request to "/projects/<from_id>/tasks/<todo_id>"
    Then the response status code should be 200
    And I resolve the course id for "<to_course>" as "<to_id>"
    When I send a POST request to "/projects/<to_id>/tasks" with JSON body:
      """
      { "id": "<todo_id>" }
      """
    Then the response status code should be 201
    And the todo "<todo_title>" should be linked to the course "<to_course>"

    Examples:
      | todo_title            | from_course | to_course |
      | Prepare presentation  | COMP 302    | SOCI 222  |

  Scenario Outline: Move a task that is not linked to the source course (Alternate flow)
    Given I resolve the course id for "<from_course>" as "<from_id>"
    And I resolve the todo id for "<todo_title>" as "<todo_id>"
    When I send a DELETE request to "/projects/<from_id>/tasks/<todo_id>"
    Then the response status code should be 404
    And I resolve the course id for "<to_course>" as "<to_id>"
    When I send a POST request to "/projects/<to_id>/tasks" with JSON body:
      """
      { "id": "<todo_id>" }
      """
    Then the response status code should be 201
    And the todo "<todo_title>" should be linked to the course "<to_course>"

    Examples:
      | todo_title          | from_course | to_course |
      | Submit reading memo | SOCI 222    | COMP 302  |

  Scenario Outline: Fail to move a task to a non-existent course (Error flow)
    Given I resolve the course id for "<from_course>" as "<from_id>"
    And I resolve the todo id for "<todo_title>" as "<todo_id>"
    When I send a DELETE request to "/projects/<from_id>/tasks/<todo_id>"
    Then the response status code should be 200
    When I send a POST request to "/projects/<invalid_to_id>/tasks" with JSON body:
      """
      { "id": "<todo_id>" }
      """
    Then the response status code should be 404

    Examples:
      | todo_title           | from_course | invalid_to_id |
      | Prepare presentation | COMP 302    | 999999        |


