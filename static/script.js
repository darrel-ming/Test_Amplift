// Attach an event listener to the "Send" button
document.getElementById("send-btn").addEventListener("click", function () {
    // Get and trim the user input from the text box
    const userInput = document.getElementById("user-input").value.trim();

    // If user input is empty, log an error and return
    if (!userInput) {
        console.error("User input is empty or invalid.");
        return;
    }

    // Display the user's message in the chatbox
    appendMessage("user-message", userInput);

    // Clear the user input field
    document.getElementById("user-input").value = "";

    // Log the user input to the server
    fetch('/log', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ type: 'user_query', message: userInput })
    });
    
    // Send the user input to the server via POST request
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(() => {
        // Initialize an EventSource instance to listen for server-sent events
        const eventSource = new EventSource('/chat');

        // Track the current response being received
        let fullResponse = '';

        // Handle incoming messages from the server
        eventSource.onmessage = (event) => {
            const data = event.data;
            if (data) {
                // Append each chunk of data to the current response
                fullResponse += data;
                
                // Update the content of the most recent bot message
                const lastBotMessage = document.querySelector('.message.bot-message:last-of-type');
                if (lastBotMessage) {
                    lastBotMessage.textContent = fullResponse; // Update the last message
                } else {
                    // If no bot message exists, create a new one
                    appendMessage("bot-message", fullResponse);
                }
            }
        };

        // Handle errors from the EventSource
        eventSource.onerror = (error) => {
            console.error('Error:', error);
            eventSource.close();
        };

        // Ensure there's an initial message container if none exists
        eventSource.onopen = () => {
            if (!document.querySelector('.message.bot-message')) {
                appendMessage("bot-message", "");
            }
        };

        // Log when the connection is closed
        eventSource.onclose = () => {
            console.log('Connection closed');
            eventSource.close();
        };
    });
});

// Function to append a message to the chatbox
function appendMessage(className, message) {
    const chatbox = document.getElementById("chatbox");
    const messageDiv = document.createElement("div");
    messageDiv.className = "message " + className;
    messageDiv.textContent = message;
    chatbox.appendChild(messageDiv);
    chatbox.scrollTop = chatbox.scrollHeight; // Scroll to the bottom
}
