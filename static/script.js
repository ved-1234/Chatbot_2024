document.getElementById('messageArea').addEventListener('submit', function(event) {
    event.preventDefault();
    
    var formData = new FormData(this);
    
    fetch('/get', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error); // Display error message
        } else {
       // Update question element
            document.getElementById('answer').textContent = data.answer; // Update answer element
        }
    })
    .catch(error => console.error('Error:', error));
});
