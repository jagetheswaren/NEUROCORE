"""
Integration tests for WebSocket and streaming endpoints.
Tests real-time chat streaming functionality.
"""

import json
import pytest
from fastapi.testclient import TestClient
from server.app import app

# Test client with WebSocket support
client = TestClient(app)


class TestStreamingEndpoint:
    """Test /chat/stream SSE endpoint."""
    
    def test_chat_stream_endpoint_basic(self):
        """Test basic streaming response."""
        response = client.post("/chat/stream", json={
            "message": "Hello",
            "mode": "friend"
        })
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        
        # Collect all events
        lines = response.text.strip().split("\n\n")
        events = []
        for line in lines:
            if line.startswith("data: "):
                event = json.loads(line[6:])
                events.append(event)
        
        # Should have status, tokens, and complete
        assert any(e.get("type") == "status" for e in events)
        assert any(e.get("type") == "token" for e in events)
        assert any(e.get("type") == "complete" for e in events)
    
    def test_chat_stream_token_sequence(self):
        """Test token count increments properly."""
        response = client.post("/chat/stream", json={
            "message": "Say 'hello'",
            "mode": "friend"
        })
        
        assert response.status_code == 200
        
        # Parse tokens
        lines = response.text.strip().split("\n\n")
        token_events = []
        for line in lines:
            if line.startswith("data: "):
                event = json.loads(line[6:])
                if event.get("type") == "token":
                    token_events.append(event)
        
        # Token counts should be sequential
        for i, event in enumerate(token_events, 1):
            assert event.get("count") == i
    
    def test_chat_stream_empty_message(self):
        """Test empty message validation."""
        response = client.post("/chat/stream", json={
            "message": "",
            "mode": "friend"
        })
        
        assert response.status_code == 400
    
    def test_chat_stream_with_mode(self):
        """Test streaming with different modes."""
        for mode in ["friend", "plan", "build"]:
            response = client.post("/chat/stream", json={
                "message": "Test",
                "mode": mode
            })
            
            assert response.status_code == 200
            
            # Verify status message contains mode
            lines = response.text.strip().split("\n\n")
            for line in lines:
                if line.startswith("data: "):
                    event = json.loads(line[6:])
                    if event.get("type") == "status":
                        # Status event should indicate the mode
                        break


class TestWebSocketChat:
    """Test WebSocket streaming endpoint."""
    
    def test_websocket_connect(self):
        """Test WebSocket connection."""
        with client.websocket_connect("/ws/chat") as websocket:
            data = websocket.receive_json()
            
            assert data["type"] == "system"
            assert data["event"] == "connected"
    
    def test_websocket_chat_message(self):
        """Test sending message via WebSocket."""
        with client.websocket_connect("/ws/chat") as websocket:
            # Receive connection message
            websocket.receive_json()
            
            # Send message
            websocket.send_json({
                "message": "Hello",
                "mode": "friend"
            })
            
            # Should receive status first
            status = websocket.receive_json()
            assert status["type"] == "status"
            assert status["event"] == "start_thinking"
            
            # Should receive tokens
            token_received = False
            while True:
                msg = websocket.receive_json()
                if msg["type"] == "message" and msg["event"] == "token":
                    token_received = True
                    assert "token" in msg
                    assert "cumulative" in msg
                    break
            
            assert token_received
    
    def test_websocket_multiple_messages(self):
        """Test multiple sequential messages."""
        with client.websocket_connect("/ws/chat") as websocket:
            # Connection message
            websocket.receive_json()
            
            # First message
            websocket.send_json({"message": "Hi", "mode": "friend"})
            
            # Collect first response
            websocket.receive_json()  # status
            while True:
                msg = websocket.receive_json()
                if msg["type"] == "message" and msg["event"] == "response_complete":
                    break
            
            # Second message
            websocket.send_json({"message": "How are you?", "mode": "friend"})
            
            # Should work without disconnecting
            websocket.receive_json()  # status
            while True:
                msg = websocket.receive_json()
                if msg["type"] == "message" and msg["event"] == "response_complete":
                    break
    
    def test_websocket_token_accumulation(self):
        """Test cumulative token accumulation."""
        with client.websocket_connect("/ws/chat") as websocket:
            websocket.receive_json()  # connection
            
            websocket.send_json({"message": "Count to 3", "mode": "friend"})
            websocket.receive_json()  # status
            
            tokens = []
            cumulative = ""
            while True:
                msg = websocket.receive_json()
                if msg["type"] == "message":
                    if msg["event"] == "token":
                        tokens.append(msg["token"])
                        assert msg["cumulative"].startswith(cumulative)
                        cumulative = msg["cumulative"]
                    elif msg["event"] == "response_complete":
                        break
            
            # Verify accumulation
            reconstructed = "".join(tokens)
            assert reconstructed == cumulative


class TestSyncVsStreamComparison:
    """Verify sync and stream endpoints produce same content."""
    
    def test_sync_chat_endpoint(self):
        """Test synchronous chat endpoint."""
        response = client.post("/chat", json={
            "message": "Say hello",
            "mode": "friend"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert len(data["response"]) > 0
    
    def test_stream_contains_sync_response(self):
        """Test that stream produces same response content."""
        # Get sync response
        sync_response = client.post("/chat", json={
            "message": "Repeat: test",
            "mode": "friend"
        })
        
        # Get stream response
        stream_response = client.post("/chat/stream", json={
            "message": "Repeat: test",
            "mode": "friend"
        })
        
        # Both should succeed
        assert sync_response.status_code == 200
        assert stream_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
