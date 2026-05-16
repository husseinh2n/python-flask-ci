import pytest
from app import app

# Pytest fixture to create a test client for the Flask application.
# This client allows making requests to the app without running a live server,
# which is ideal for unit testing.
@pytest.fixture
def client():
    # Configure the app for testing.
    # Setting 'TESTING' to True disables error catching during request handling,
    # so errors propagate to the test client and can be asserted.
    app.config['TESTING'] = True
    # Establish an application context before the tests run.
    # This is necessary for some Flask features (like current_app) to work correctly.
    with app.test_client() as client:
        # Yield the client to the test functions.
        # Code after 'yield' will run as teardown after the test completes.
        yield client

def test_hello_world_get_request(client):
    """
    Verifies that the root endpoint ('/') returns a 200 OK status
    and the expected 'Hello, World!' message.
    This is a happy path unit test for the main endpoint.
    """
    # Make a GET request to the root URL using the test client.
    response = client.get('/')
    # Assert that the HTTP status code is 200 (OK).
    assert response.status_code == 200
    # Assert that the response data contains the expected string.
    # response.data is bytes, so we compare with a bytes literal.
    assert b'Hello, World!' in response.data

def test_greet_name_get_request(client):
    """
    Verifies that the '/greet/<name>' endpoint returns a 200 OK status
    and a personalized greeting message.
    This unit tests a dynamic route with a path parameter.
    """
    test_name = "Alice"
    # Make a GET request to the dynamic greet URL.
    response = client.get(f'/greet/{test_name}')
    # Assert that the HTTP status code is 200 (OK).
    assert response.status_code == 200
    # Assert that the response data contains the personalized greeting.
    assert f'Hello, {test_name}!'.encode('utf-8') in response.data

def test_non_existent_route_returns_404(client):
    """
    Verifies that accessing a non-existent route returns a 404 Not Found status.
    This is a failure path unit test for invalid URLs within the application.
    """
    # Make a GET request to a URL that does not exist in the application.
    response = client.get('/nonexistent-page')
    # Assert that the HTTP status code is 404 (Not Found).
    assert response.status_code == 404
    # Optionally, check for a default 404 message if Flask provides one.
    # Flask's default 404 page often contains "Not Found" or "404".
    assert b'Not Found' in response.data or b'404' in response.data