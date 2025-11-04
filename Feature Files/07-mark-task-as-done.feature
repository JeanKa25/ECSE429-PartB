Feature: Mark a task as done

  As a student, I want to mark a task as done so that I can track my progress.

  Background:
    Given the server is running

  Scenario Outline: Mark an existing task as done (Normal flow)
    Given a todo titled "<title>" exists and is saved as "todoId"
    When I mark the todo "todoId" as done
    Then the response status code should be 200

    Examples:
      | title                 |
      | Write lab report      |
      | Prepare presentation  |

  Scenario Outline: Mark an already done task again (Alternate flow)
    Given a todo titled "<title>" exists and is saved as "todoId"
    When I mark the todo "todoId" as done
    Then the response status code should be 200
    When I mark the todo "todoId" as done
    Then the response status code should be 200

    Examples:
      | title                 |
      | Submit reading memo   |

  Scenario Outline: Mark a non-existent task as done (Error flow)
    Given id <bad_id> doesn't exist
    When I mark the todo "<bad_id>" as done
    Then the response status code should be 404

    Examples:
      | bad_id |
      | 999999 |
      | 888888 |


