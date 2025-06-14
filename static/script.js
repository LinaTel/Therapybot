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

        msgBox.appendChild(textSpan);
      }

      chatHistory.appendChild(msgBox);
    });

    chatHistory.scrollTop = chatHistory.scrollHeight;
  } catch (error) {
    console.error("Error loading initial chat history:", error);
  }
}

async function sendMessage() {
  const userInputField = document.getElementById("userInput");
  const userInput = userInputField.value.trim();
  const chatHistory = document.getElementById("chatHistory");

  if (!userInput) return;

  // Show user's message
  const userMessage = document.createElement("div");
  userMessage.classList.add("message", "user-message");
  userMessage.innerText = userInput;
  chatHistory.appendChild(userMessage);

  // Create AI response box with loader
  const responseBox = document.createElement("div");
  responseBox.classList.add("message", "ai-message");

  const loader = document.createElement("div");
  loader.classList.add("loader-wrapper");
  loader.innerHTML = `
    <div class="circle"></div>
    <div class="circle"></div>
    <div class="circle"></div>
    <div class="shadow"></div>
    <div class="shadow"></div>
    <div class="shadow"></div>
  `;


    const mascotImg = document.createElement("img");
  mascotImg.src = "/static/images/studybuddy cat.png";
  mascotImg.classList.add("ai-mascot");

  responseBox.appendChild(loader);

  chatHistory.appendChild(responseBox);
  chatHistory.scrollTop = chatHistory.scrollHeight;

  // Clear input field
  userInputField.value = "";

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: userInput })
    });

    const data = await res.json();

    responseBox.removeChild(loader);

    const textSpan = document.createElement("span");
    textSpan.classList.add("ai-text");

    if (data.response) {
      textSpan.innerText = data.response.trim();
    } else {
      textSpan.innerText = "Error: Could not get a response.";
    }

    responseBox.appendChild(textSpan);
  } catch (error) {
    loader.innerHTML = "Error contacting the server.";
    console.error("Fetch error:", error);
  }

  chatHistory.scrollTop = chatHistory.scrollHeight;
}