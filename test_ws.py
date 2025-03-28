import asyncio
import websockets
import json
import requests

# API Base URL
BASE_URL = "http://127.0.0.1:8000"

# User credentials
USERS = {
    "User1": {"username": "user1", "password": "pass1"},
    "User2": {"username": "user2", "password": "pass2"},
}

async def user_test(user_name, token):
    """ Connects to WebSocket, sends messages, and listens for responses. """
    ws_url = f"ws://127.0.0.1:8000/ws/sessionA?token={token}"

    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ {user_name} connected")

            # Wait a bit to ensure the server is ready
            await asyncio.sleep(1)

            # Send multiple messages
            for i in range(3):
                message = json.dumps({"user": user_name, "message": f"Hello {i} from {user_name}"})
                await websocket.send(message)
                print(f"📤 {user_name} sent: {message}")

                # Listen for a response (or timeout after 5s)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    print(f"📥 {user_name} received: {response}")
                except asyncio.TimeoutError:
                    print(f"⏳ {user_name} did not receive a response in time.")

            print(f"🔌 {user_name} closing connection.")

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ {user_name} WebSocket closed unexpectedly: {e}")
    except Exception as e:
        print(f"⚠️ {user_name} Error: {e}")


def get_token(username, password):
    """ Fetch JWT access token from the API """
    response = requests.post(f"{BASE_URL}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"❌ Failed to get token for {username}: {response.json()}")
        return None

async def test_websocket():
    """ Runs WebSocket tests for multiple users concurrently. """
    tokens = {user: get_token(data["username"], data["password"]) for user, data in USERS.items()}
    if None in tokens.values():
        print("⚠️ Error: One or more users failed to authenticate. Exiting.")
        return

    await asyncio.gather(*(user_test(user, token) for user, token in tokens.items()))

if __name__ == "__main__":
    asyncio.run(test_websocket())
# In this test script, we have a few key components: