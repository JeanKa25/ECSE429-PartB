Feature: Add a Task to a Course Todo List
  As a student, I want to add a task to a course to-do list so that I can organize and keep track of my work.

  Background:
    Given the server is running
    And the following todos exist:
      | title                    | doneStatus | description                          |
      | Write lab report         | false      | Section 3 needs revision             |
      | Prepare presentation     | false      | Slides due next Thursday               |
      | Submit reading summary   | false      | Chapter 4 of Urban Sociology         |
    And the following course todo lists exist:
      | title    | completed | description         | active |
      | COMP 302 | false     | Programming Languages | true   |
      | SOCI 222 | false     | Urban Sociology       | true   |

  Scenario Outline: Add an existing todo to a course todo list (Normal flow)
    Given the Todo API endpoint "/projects/<course_id>/tasks" is available
    When I send a POST request to "/projects/<course_id>/tasks" with JSON body:
      """
      {
        "id": "<todo_id>"
      }
      """
    Then the response status code should be 201
    And the todo with id "<todo_id>" should now belong to the project "<course>"

    Examples:
      | course_id | course    | todo_id | title                 |
      | 1         | COMP 302  | 2       | Prepare presentation  |
      | 2         | SOCI 222  | 3       | Submit reading summary |

  Scenario Outline: Add a new todo to a course todo list that has no prior tasks (Alternate flow)
    Given the student creates a new course todo list with title "<course>" and description "<description>"
    And the Todo API endpoint "/todos" is available
    When I send a POST request to "/todos" with JSON body:
      """
      {
        "title": "<title>",
        "description": "<task_description>"
      }
      """
    And I send a POST request to "/projects/<course_id>/tasks" with JSON body:
      """
      {
        "id": "<todo_id>"
      }
      """
    Then the response status code should be 201
    And the new todo "<title>" should be linked to the course "<course>"

    Examples:
      | course     | description           | title                | task_description             | course_id | todo_id |
      | MATH 240   | Discrete Structures   | Complete assignment  | Submit proof by Wednesday    | 3         | 4       |
      | HIST 210   | Modern History        | Write essay draft    | Focus on WWII section        | 4         | 5       |

  Scenario Outline: Add a todo using an invalid id to a course todo list (Error flow)
    Given no todo exists with id "<todo_id>"
    When I send a POST request to "/projects/<course_id>/tasks" with JSON body:
      """
      {
        "id": "<todo_id>"
      }
      """
    Then the response status code should be 404
    And the response message should contain "<error_message>"

    Examples:
      | course_id | todo_id | error_message                                                  |
      | 1         | 999     | Could not find parent thing for relationship todos/999/tasksof |
      | 2         | 888     | Could not find parent thing for relationship todos/888/tasksof |
