import asyncio
import json
from typing import Dict, List, Optional
from fastapi import Request
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone

from services.notifications_service import NotificationsService


class SSEManager:
    def __init__(self):
        self._connections: Dict[str, List[asyncio.Queue]] = {}
        self._notifications_service: Optional[NotificationsService] = None

    def set_notifications_service(self, notifications_service: NotificationsService):
        """Set the notifications service for broadcasting"""
        self._notifications_service = notifications_service

    async def add_connection(self, user_id: str, request: Request) -> StreamingResponse:
        """Add a new SSE connection for a user"""
        if user_id not in self._connections:
            self._connections[user_id] = []
        
        # Create a queue for this connection
        queue = asyncio.Queue()
        self._connections[user_id].append(queue)
        
        # Subscribe to notifications service if available
        if self._notifications_service:
            self._notifications_service.subscribe_to_notifications(user_id, queue)
        
        async def event_generator():
            try:
                while True:
                    # Check if client disconnected
                    if await request.is_disconnected():
                        break
                    
                    try:
                        # Wait for a message with timeout
                        message = await asyncio.wait_for(queue.get(), timeout=30.0)
                        yield message
                    except asyncio.TimeoutError:
                        # Send keep-alive ping
                        yield "data: {\"type\": \"ping\", \"timestamp\": \"" + datetime.now(timezone.utc).isoformat() + "\"}\n\n"
                    except Exception as e:
                        print(f"Error in SSE connection: {e}")
                        break
            finally:
                # Clean up connection
                self._remove_connection(user_id, queue)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )

    def _remove_connection(self, user_id: str, queue: asyncio.Queue):
        """Remove a connection from the manager"""
        if user_id in self._connections:
            try:
                self._connections[user_id].remove(queue)
                if not self._connections[user_id]:
                    del self._connections[user_id]
            except ValueError:
                pass  # Queue not found

    async def send_to_user(self, user_id: str, data: dict):
        """Send data to all connections for a specific user"""
        if user_id in self._connections:
            message = f"data: {json.dumps(data)}\n\n"
            connections_to_remove = []
            
            for queue in self._connections[user_id]:
                try:
                    await queue.put(message)
                except Exception:
                    # Connection is closed, mark for removal
                    connections_to_remove.append(queue)
            
            # Remove closed connections
            for queue in connections_to_remove:
                self._remove_connection(user_id, queue)

    async def send_to_all(self, data: dict):
        """Send data to all connected users"""
        message = f"data: {json.dumps(data)}\n\n"
        all_connections_to_remove = []
        
        for user_id, queues in self._connections.items():
            user_connections_to_remove = []
            for queue in queues:
                try:
                    await queue.put(message)
                except Exception:
                    user_connections_to_remove.append(queue)
            
            # Remove closed connections for this user
            for queue in user_connections_to_remove:
                self._remove_connection(user_id, queue)

    def get_connection_count(self, user_id: str = None) -> int:
        """Get the number of active connections"""
        if user_id:
            return len(self._connections.get(user_id, []))
        return sum(len(queues) for queues in self._connections.values())

    def get_connected_users(self) -> List[str]:
        """Get list of users with active connections"""
        return list(self._connections.keys())


# Global SSE manager instance
sse_manager = SSEManager()
