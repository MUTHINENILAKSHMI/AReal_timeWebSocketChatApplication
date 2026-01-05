from fastapi import FastAPI, WebSocket
import uvicorn
app = FastAPI()
@app.get("/")
async def read_root():
    return {"message": "chatterbox milestone 1 - WebSocket server Running"}
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Step 1: Accept the websocket connection
    await websocket.accept()
    print("Client connected")
    # Step 2: Keep listening for messages
    while True:
        try:
            message = await websocket.receive_text()
            print(f"Received : {message}")

            # Step 3: Echo message back to client
            await websocket.send_text(f"server: you said -> {message}")
        except Exception as e:
            print("Client disconnected!", e)
            break
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)