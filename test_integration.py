import pytest
import requests
import subprocess
import time
import os

# Define the port where the Flask app is expected to run inside Docker Compose.
# This should match the exposed port in docker-compose.yml (e.g., 5000:5000).
FLASK_APP_PORT = 5000
# Base URL for the Flask application running in Docker.
FLASK_APP_BASE_URL = f"http://localhost:{FLASK_APP_PORT}"

# Pytest fixture to manage the Docker Compose services lifecycle.
# 'scope="session"' means this fixture will run once per test session,
# starting containers before any tests run and stopping them after all tests complete.
@pytest.fixture(scope="session")
def docker_compose_up_down():
    """
    Starts Docker Compose services before tests and stops them after tests.
    It also includes a waiting mechanism to ensure the Flask application
    inside the container is fully available before tests begin.
    """
    print("\n--- Starting Docker Compose services ---")
    try:
        # Use subprocess to run 'docker compose up -d' (Docker Compose V2)
        # The 'docker compose' command (without a hyphen) is the modern way to
        # interact with Docker Compose as a Docker CLI plugin, and is reliably
        # available on GitHub Actions runners.
        # '-d' runs containers in detached mode (in the background).
        # '--build' ensures images are rebuilt, useful for fresh tests or changes.
        # 'check=True' raises an exception if the command fails.
        # 'capture_output=True' captures stdout/stderr, preventing it from cluttering console.
        subprocess.run(["docker", "compose", "up", "-d", "--build"], check=True, capture_output=True)

        # Wait for the Flask application to be ready.
        # This is crucial for integration tests to avoid connection errors
        # if the tests try to connect before the app is fully initialized.
        max_retries = 30
        retry_delay_seconds = 2
        for i in range(max_retries):
            try:
                print(f"Attempt {i+1}/{max_retries}: Checking Flask app availability at {FLASK_APP_BASE_URL}...")
                # Make a small timeout request to quickly check connectivity.
                response = requests.get(FLASK_APP_BASE_URL, timeout=1)
                if response.status_code == 200:
                    print("Flask app is up and running!")
                    break # Exit loop if app is ready
            except requests.exceptions.ConnectionError:
                print("Flask app not yet available, retrying...")
            except requests.exceptions.Timeout:
                print("Connection timed out, retrying...")
            time.sleep(retry_delay_seconds)
        else:
            # If the loop completes without the app becoming available, fail the tests.
            pytest.fail(f"Flask app did not become available after {max_retries * retry_delay_seconds} seconds.")

        # Yield control to the tests.
        # All tests using this fixture will run after this point.
        yield

    finally:
        # This block runs after all tests using this fixture have completed,
        # ensuring cleanup even if tests fail.
        print("\n--- Stopping Docker Compose services ---")
        # Use subprocess to run 'docker compose down' (Docker Compose V2)
        # '--volumes' removes named volumes declared in the `volumes` section of the Compose file
        # and anonymous volumes attached to containers.
        # '--rmi all' removes all images used by any service, ensuring a clean slate for next run.
        subprocess.run(["docker", "compose", "down", "--volumes", "--rmi", "all"], check=True, capture_output=True)
        print("--- Docker Compose services stopped ---")

# All tests in this file will implicitly use the 'docker_compose_up_down' fixture
# because it's defined in the same file and has a session scope.
# If you wanted to explicitly depend on it, you'd add it as an argument:
# def test_something(docker_compose_up_down):

def test_integration_hello_world_endpoint(docker_compose_up_down):
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

def test_integration_greet_name_endpoint(docker_compose_up_down):
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

def test_integration_non_existent_route_returns_404(docker_compose_up_down):
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