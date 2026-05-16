from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    """
    Root endpoint that returns a simple 'Hello, World!' message.
    """
    return 'Hello, World!'

@app.route('/greet/<name>')
def greet(name):
    """
    Endpoint that returns a personalized greeting.
    """
    return f'Hello, {name}!'

if __name__ == '__main__':
    # Run the Flask app in debug mode on all available interfaces
    app.run(debug=True, host='0.0.0.0')