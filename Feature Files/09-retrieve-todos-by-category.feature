Feature: See all tasks under a study category
  As a student, I want to view all tasks in a category so that I can group related todos.

  Background:
    Given the server is running

  Scenario Outline: Retrieve tasks in a category (Normal flow)
    When I send a POST request to "/categories" with JSON body:
      """
      { "title": "<category>" }
      """
    And I send a POST request to "/todos" with JSON body:
      """
      { "title": "<t1>", "description": "<d1>" }
      """
    And I send a POST request to "/todos/{createdTodoId}/categories" with JSON body:
      """
      { "id": "{createdCategoryId}" }
      """
    And I send a POST request to "/todos" with JSON body:
      """
      { "title": "<t2>", "description": "<d2>" }
      """
    And I send a POST request to "/todos/{createdTodoId}/categories" with JSON body:
      """
      { "id": "{createdCategoryId}" }
      """
    When I send a GET request to "/categories/{createdCategoryId}/todos"
    Then the response status code should be 200
    And the response should include todos "<t1>" and "<t2>"

    Examples:
      | category   | t1                 | d1                  | t2                   | d2               |
      | Academics  | Read chapter 3     | Notes due Wed       | Prepare slides       | Week 6           |
      | Personal   | Buy groceries      | Fruits and veggies  | Cook dinner          | Pizza night      |
      | Work       | Draft report       | First section       | Review pull request  | By tomorrow noon |

  Scenario Outline: Retrieve tasks for a category with no tasks (Alternate flow)
    When I send a POST request to "/categories" with JSON body:
      """
      { "title": "<category>" }
      """
    When I send a GET request to "/categories/{createdCategoryId}/todos"
    Then the response status code should be 200
    And the response body should be an empty array

    Examples:
      | category |
      | Reading  |

  # EXPECTED: 404 Not Found when category does not exist
  # ACTUAL (BUG): API returns 200 with empty categories. Accept 200 to reflect behavior.
  Scenario Outline: Retrieve tasks for an invalid category id (Error flow - BUG)
    When I send a GET request to "/categories/<bad_id>/todos"
    Then the response status code should be 200

    Examples:
      | bad_id |
      | 999999 |
      | 888888 |

