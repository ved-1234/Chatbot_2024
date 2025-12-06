document.getElementById("messageArea").addEventListener("submit", function(e) {
    e.preventDefault();

    let userMessage = document.getElementById("text").value;

    fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ msg: userMessage })   // IMPORTANT FIX
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);

        // Show bot answer
        let botReply = `
            <div class="d-flex justify-content-start mb-4">
                <div class="msg_cotainer">${data.answer}</div>
            </div>
        `;
        document.getElementById("messageFormeight").innerHTML += botReply;

        // Show retrieved context in HTML
        if (data.context) {
            let ctxHtml = "<div class='retrieved'><b>Retrieved Text:</b><br>";
            ctxHtml += data.context.map(c => `<p>${c}</p>`).join("");
            ctxHtml += "</div>";
            document.getElementById("messageFormeight").innerHTML += ctxHtml;
        }
    })
    .catch(err => console.error(err));
});
