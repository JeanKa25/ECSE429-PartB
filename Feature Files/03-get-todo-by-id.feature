Feature: Look up a course task by id

  As a student, I want to look up a specific course task by its id, so that I can quickly see its details.

  Background:
    Given the server is running

  Scenario Outline: Retrieve an existing task by id (Normal flow)
    Given a valid todo id exists and is saved as "todoId"
    When I send a get-by-id GET request to "/todos/{todoId}"
    Then the response status code should be 200

    Examples:
      | run |
      | 1   |
      | 2   |

  Scenario Outline: Retrieve a task immediately after creation (Alternate flow)
    Given a new todo "<title>" is created and its id is saved as "newTodoId"
    When I send a get-by-id GET request to "/todos/{newTodoId}"
    Then the response status code should be 200

    Examples:
      | title               |
      | Read chapter 4      |
      | Email TA            |

  Scenario Outline: Get a task by an invalid id (Error flow)
    Given id <bad_id> doesn't exist
    When I send a GET request to "/todos/<bad_id>"
    Then the response status code should be 404

    Examples:
      | bad_id |
      | 999999 |
      | 888888 |

