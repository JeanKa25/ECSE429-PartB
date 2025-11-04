Feature: Update details of a course task

  As a student, I want to update a task’s title or description so that I keep my course work up to date.

  Background:
    Given the server is running
    And the following todos exist for update:
      | title               | doneStatus | description              |
      | Draft project plan  | false      | Outline key milestones   |

  Scenario Outline: Update a task with valid data using PUT (Normal flow)
    Given an update todo id exists and is saved as "todoId"
    When I send an update PUT request to "/todos/{todoId}" with JSON body:
      """
      {
        "title": "<new_title>",
        "description": "<new_description>"
      }
      """
    Then the update response status code should be 200

    Examples:
      | new_title        | new_description         |
      | Updated title    | Updated description     |
      | Renamed task     | Clarified instructions  |

  Scenario Outline: Fix a task with partial data using POST (Alternate flow)
    Given an update todo id exists and is saved as "todoId"
    When I send an update POST request to "/todos/{todoId}" with JSON body:
      """
      {
        "description": "<only_description>"
      }
      """
    Then the update response status code should be 200

    Examples:
      | only_description        |
      | Only description updated|

  Scenario Outline: Update a task that does not exist (Error flow)
    Given update id <bad_id> doesn't exist
    When I send an update PUT request to "/todos/<bad_id>" with JSON body:
      """
      {
        "title": "Won't matter",
        "description": "This id does not exist"
      }
      """
    Then the update response status code should be 404

    Examples:
      | bad_id |
      | 999999 |
      | 888888 |

