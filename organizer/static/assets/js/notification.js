const socket = new WebSocket("ws://localhost:8000/ws/notifications/");

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    alert("New Notification: " + data.message);
};

socket.onclose = function(event) {
    console.log("WebSocket closed.");
}