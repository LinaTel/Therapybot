async function sendMessage() {
  const userInput = document.getElementById("userInput").value;
  const chatHistory = document.getElementById("chatHistory");

  if (!userInput.trim()) {
    return;  // Don't send if input is empty
  }

  // Display the user's message in the chat history
  const userMessage = document.createElement("div");
  userMessage.classList.add("message", "user-message");
  userMessage.innerText = userInput;
  chatHistory.appendChild(userMessage);

  // Scroll to the bottom to show new message
  chatHistory.scrollTop = chatHistory.scrollHeight;

  // Send user input to the Flask backend
  const responseBox = document.createElement("div");
  responseBox.classList.add("message", "ai-message");
  responseBox.innerText = "Thinking...";  // Temporary message while waiting
  chatHistory.appendChild(responseBox);
  chatHistory.scrollTop = chatHistory.scrollHeight;

  try {
    // Send the user input to the Flask server
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: userInput })
    });

    const data = await res.json();

    if (data.response) {
      // Replace "Thinking..." with the AI's response
      responseBox.innerText = data.response.trim();
    } else {
      responseBox.innerText = "Error: Could not get a response.";
    }
  } catch (error) {
    responseBox.innerText = "Error contacting the server.";
    console.error(error);
  }

  // Scroll to the bottom to show AI's response
  chatHistory.scrollTop = chatHistory.scrollHeight;
}
