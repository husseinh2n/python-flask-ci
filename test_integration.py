import pytest
import requests
# Removed subprocess, time, and os imports as Docker Compose lifecycle is now managed by CI.

# Define the port where the Flask app is expected to run inside Docker Compose.
# This should match the exposed port in docker-compose.yml (e.g., 5000:5000).
FLASK_APP_PORT = 5000
# Base URL for the Flask application running in Docker.
FLASK_APP_BASE_URL = f"http://localhost:{FLASK_APP_PORT}"

# The docker_compose_up_down fixture has been removed.
# Docker Compose services are now started and stopped directly by the GitHub Actions workflow.
# Tests in this file will assume the Flask application is already running and accessible
# at FLASK_APP_BASE_URL when they are executed.

def test_integration_hello_world_endpoint():
    """
    Verifies that the Flask app, when running in its Docker container via Docker Compose,
    responds correctly to a GET request on the root endpoint ('/').
    This is a happy path integration test, checking the entire stack.
    """
    print(f"Testing GET {FLASK_APP_BASE_URL}/")
    response = requests.get(FLASK_APP_BASE_URL)
    # Assert that the HTTP status code is 200 (OK).
    assert response.status_code == 200
    # Assert that the response text contains the expected message.
    assert "Hello, World!" in response.text

def test_integration_greet_name_endpoint():
    """
    Verifies that the Flask app, when running in Docker, responds correctly
    to a GET request on the '/greet/<name>' endpoint.
    This tests a dynamic route in an integrated environment, ensuring routing
    and response generation work as expected within the container.
    """
    test_name = "DockerUser"
    url = f"{FLASK_APP_BASE_URL}/greet/{test_name}"
    print(f"Testing GET {url}")
    response = requests.get(url)
    assert response.status_code == 200
    assert f"Hello, {test_name}!" in response.text

def test_integration_non_existent_route_returns_404():
    """
    Verifies that accessing a non-existent route on the Dockerized Flask app
    returns a 404 Not Found status.
    This is a failure path integration test, ensuring the web server and Flask
    handle invalid URLs gracefully.
    """
    non_existent_url = f"{FLASK_APP_BASE_URL}/this-page-does-not-exist"
    print(f"Testing GET {non_existent_url}")
    response = requests.get(non_existent_url)
    # Assert that the HTTP status code is 404 (Not Found).
    assert response.status_code == 404
    # Optionally, check for a default 404 message in the response text.
    assert "Not Found" in response.text or "404" in response.text