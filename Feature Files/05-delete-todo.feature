Feature: Remove a course task

  As a student, I want to remove tasks that are no longer relevant so that I keep my todo list clean.

  Background:
    Given the server is running
    And the following todos exist for delete:
      | title                 | doneStatus | description                  |
      | Old draft to remove   | false      | No longer needed             |
      | Obsolete reading note | true       | Completed last semester      |

  Scenario Outline: Delete a task by valid id (Normal flow)
    Given a delete todo id exists and is saved as "todoId"
    When I send a delete DELETE request to "/todos/{todoId}"
    Then the delete response status code should be 200

    Examples:
      | run |
      | 1   |

  Scenario Outline: Delete an already deleted task (Alternate flow)
    Given a delete todo id exists and is saved as "deletedTodoId"
    When I send a delete DELETE request to "/todos/{deletedTodoId}"
    Then the delete response status code should be 200
    When I send a delete DELETE request to "/todos/{deletedTodoId}"
    Then the delete response status code should be 404

    Examples:
      | run |
      | 1   |

  Scenario Outline: Delete a non-existent task (Error flow)
    Given delete id <bad_id> doesn't exist
    When I send a delete DELETE request to "/todos/<bad_id>"
    Then the delete response status code should be 404

    Examples:
      | bad_id |
      | 999999 |
      | 888888 |

