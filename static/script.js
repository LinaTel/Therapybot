document.addEventListener("DOMContentLoaded", loadInitialMessage);

async function loadInitialMessage() {
  try {
    const res = await fetch("/session-history");
    const data = await res.json();

    const chatHistory = document.getElementById("chatHistory");

    data.history.forEach((msg) => {
      const msgBox = document.createElement("div");
      msgBox.classList.add("message", msg.role === "user" ? "user-message" : "ai-message");

      if (msg.role === "user") {
        msgBox.innerText = msg.content;
      } else {
        // Create span for AI text
        const textSpan = document.createElement("span");
        textSpan.classList.add("ai-text");
        textSpan.innerText = msg.content;

        // Create mascot image
        const mascotImg = document.createElement("img");
        mascotImg.src = "/static/images/studybuddy cat.png";
        mascotImg.classList.add("ai-mascot");

        msgBox.appendChild(textSpan);
        msgBox.appendChild(mascotImg);
      }

      chatHistory.appendChild(msgBox);
    });

    chatHistory.scrollTop = chatHistory.scrollHeight;
  } catch (error) {
    console.error("Error loading initial chat history:", error);
  }
}

async function sendMessage() {
  const userInput = document.getElementById("userInput").value;
  const chatHistory = document.getElementById("chatHistory");

  if (!userInput.trim()) {
    return; 
  }

  // Display the user's message
  const userMessage = document.createElement("div");
  userMessage.classList.add("message", "user-message");
  userMessage.innerText = userInput;
  chatHistory.appendChild(userMessage);

  // Scroll down
  chatHistory.scrollTop = chatHistory.scrollHeight;

  // Create AI response box with mascot
  const responseBox = document.createElement("div");
  responseBox.classList.add("message", "ai-message");

  const textSpan = document.createElement("span");
  textSpan.classList.add("ai-text");
  textSpan.innerText = "Thinking...";

  const mascotImg = document.createElement("img");
  mascotImg.src = "/static/images/studybuddy cat.png"; 
  mascotImg.classList.add("ai-mascot");

  responseBox.appendChild(textSpan);
  responseBox.appendChild(mascotImg);
  chatHistory.appendChild(responseBox);
  chatHistory.scrollTop = chatHistory.scrollHeight;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: userInput })
    });

    const data = await res.json();

    if (data.response) {
      textSpan.innerText = data.response.trim();
    } else {
      textSpan.innerText = "Error: Could not get a response.";
    }
  } catch (error) {
    textSpan.innerText = "Error contacting the server.";
    console.error(error);
  }

  // Scroll down
  chatHistory.scrollTop = chatHistory.scrollHeight;

  // Clear input
  document.getElementById("userInput").value = "";
}