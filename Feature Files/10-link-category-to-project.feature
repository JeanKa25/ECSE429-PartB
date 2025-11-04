Feature: Link a study category to a course list

  As a student, I want to tag a course list with a category so that I can easily organize and filter my coursework by topic.

  Background:
    Given the server is running

  Scenario Outline: Link a newly created category to a newly created course (Normal flow)
    When I send a POST request to "/projects" with JSON body:
      """
      { "title": "<course>", "description": "<description>" }
      """
    And I send a POST request to "/categories" with JSON body:
      """
      { "title": "<category>" }
      """
    And I send a POST request to "/projects/{createdProjectId}/categories" with JSON body:
      """
      { "id": "{createdCategoryId}" }
      """
    Then the response status code should be 201
    And the project should have category "<category>"

    Examples:
      | course      | description          | category   |
      | COMP 302    | Programming Language | Academics  |
      | SOCI 222    | Urban Sociology      | Reading    |

  Scenario Outline: Re-link the same category to the same course (Alternate flow)
    When I send a POST request to "/projects" with JSON body:
      """
      { "title": "<course>", "description": "<description>" }
      """
    And I send a POST request to "/categories" with JSON body:
      """
      { "title": "<category>" }
      """
    And I send a POST request to "/projects/{createdProjectId}/categories" with JSON body:
      """
      { "id": "{createdCategoryId}" }
      """
    And I send a POST request to "/projects/{createdProjectId}/categories" with JSON body:
      """
      { "id": "{createdCategoryId}" }
      """
    Then the response status code should be 201

    Examples:
      | course   | description   | category |
      | ENGL 202 | Literature    | Reading  |

  Scenario Outline: Link a non-existent category id to a course (Error flow)
    When I send a POST request to "/projects" with JSON body:
      """
      { "title": "<course>", "description": "<description>" }
      """
    And I send a POST request to "/projects/{createdProjectId}/categories" with JSON body:
      """
      { "id": "999999" }
      """
    Then the response status code should be 404

    Examples:
      | course   | description   |
      | MATH 141 | Calculus II   |


