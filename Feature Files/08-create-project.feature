Feature: Create a new course list
  As a student, I want to create a course list so that I can group related tasks together.

  Background:
    Given the server is running

  Scenario Outline: Create a project with valid title and description (Normal flow)
    Given the Todo API endpoint "/projects" is available
    When I send a POST request to "/projects" with JSON body:
      """
      {
        "title": "<title>",
        "description": "<description>"
      }
      """
    Then the response status code should be 201

    Examples:
      | title               | description                               |
      | Groceries Shopping  | Shopping and meal preparation              |
      | ECSE429 Course      | Coursework and assignments                 |
      | Communication       | Emails and calls                           |

  Scenario Outline: Create a project with only title, omitting optional fields (Alternate flow)
    Given the Todo API endpoint "/projects" is available
    When I send a POST request to "/projects" with JSON body:
      """
      {
        "title": "<title>"
      }
      """
    Then the response status code should be 201

    Examples:
      | title               |
      | Groceries Shopping  |
      | ECSE429 Course      |
      | Communication       |

  Scenario Outline: Create a project with malformed JSON (Error flow)
    Given the Todo API endpoint "/projects" is available
    When I send a POST request to "/projects" with raw payload:
      """
      <malformed_json>
      """
    Then the response status code should be 400

    Examples:
      | malformed_json                                                    |
      | {"title": "Groceries Shopping", "description": "Shopping and meal preparation"     |
      | {title: "ECSE429 Course", description: "Coursework and assignments"          |
      | {"title": "Communication", "description": "Emails and calls", }


