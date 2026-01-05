from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.usernames = {}

    async def connect(self, websocket: WebSocket, username: str):
        self.active_connections.append(websocket)
        self.usernames[websocket] = username

    def disconnect(self, websocket: WebSocket):
        username = self.usernames.get(websocket, "Someone")
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.usernames:
            del self.usernames[websocket]
        return username

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active_connections:
            try:
                await ws.send_json(data)
            except:
                dead.append(ws)

        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


@app.get("/")
async def root():
    return {"message": "Server running"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    username = "Anonymous"

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "join":
                username = data.get("username", "Anonymous")
                await manager.connect(websocket, username)

                print(f"{username} joined")

                await manager.broadcast({
                    "type": "system",
                    "message": f"{username} joined the chat 👋"
                })

            elif msg_type == "chat":
                message = data.get("message", "").strip()
                if message:
                    print(f"[CHAT] {username}: {message}")
                    await manager.broadcast({
                        "type": "chat",
                        "username": username,
                        "message": message
                    })

    except WebSocketDisconnect:
        left = manager.disconnect(websocket)
        print(f"{left} left")

        await manager.broadcast({
            "type": "system",
            "message": f"{left} left the chat ❌"
        })
