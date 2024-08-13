import logging
from openai import OpenAI
from flask import Flask, render_template, request, Response, stream_with_context

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)
client = None
user_message = ''

def generate_response(user_input):
    """
    Simulates generating a response from OpenAI's GPT model.
    Streams the response to the client in real-time.
    """
    logging.info(f"User Input: {user_input}")
    try:
        messages = [
            {
                "role": "user",
                "content": user_input
            }
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield f"data: {content}\n\n"  # Format the response as server-sent events
                logging.info(f"Bot Response Chunk: {content}")
    except Exception as e:
        logging.error(f"Error in generate_response: {e}")
        yield "data: I'm sorry, I don't understand that.\n\n"

@app.route('/')
def index():
    """
    Renders the main chat interface.
    """
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """
    Handles chat interactions. 
    - POST request: Stores the user's message.
    - GET request: Streams the AI response to the client.
    """
    global user_message
    if request.method == 'POST':
        # Store the user's message from the POST request
        user_message = request.json.get("message")
        logging.info(f"User Message Received: {user_message}")
        return '', 200
    elif request.method == 'GET':
        # Stream the response to the client for the GET request
        return Response(stream_with_context(generate_response(user_message)), mimetype='text/event-stream')

@app.route('/log', methods=['POST'])
def log():
    """
    Logs various types of messages (user queries, bot responses, and errors).
    """
    log_data = request.json
    log_type = log_data.get("type")
    message = log_data.get("message")

    if log_type == 'user_query':
        logging.info(f"User Query: {message}")
    elif log_type == 'bot_response':
        logging.info(f"Bot Response: {message}")
    elif log_type == 'error':
        logging.error(f"Error: {message}")

    return '', 200


if __name__ == '__main__':
    # Load the OpenAI API key and initialize the client
    try:
        with open('openai_key.dat') as f:
            key = f.read().strip()
            client = OpenAI(api_key=key)
    except Exception as e:
        logging.error(f"Error occurred while loading OpenAI key: {e}")
    
    app.run()
