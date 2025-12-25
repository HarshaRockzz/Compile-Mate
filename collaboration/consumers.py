"""
WebRTC Signaling Consumer for Real-time Video/Audio Communication
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)


class WebRTCSignalingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for WebRTC signaling
    Handles offer, answer, and ICE candidate exchange between peers
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'webrtc_{self.room_id}'
        self.user = self.scope['user']
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify room that a new user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id if self.user.is_authenticated else 'anonymous',
                'username': self.user.username if self.user.is_authenticated else 'Anonymous',
                'channel_name': self.channel_name
            }
        )
        
        logger.info(f"User {self.user.username if self.user.is_authenticated else 'Anonymous'} connected to room {self.room_id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Notify room that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.user.id if self.user.is_authenticated else 'anonymous',
                'username': self.user.username if self.user.is_authenticated else 'Anonymous',
                'channel_name': self.channel_name
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"User {self.user.username if self.user.is_authenticated else 'Anonymous'} disconnected from room {self.room_id}")
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            logger.debug(f"Received message type: {message_type} from {self.user.username if self.user.is_authenticated else 'Anonymous'}")
            
            # Route message based on type
            if message_type == 'offer':
                await self.handle_offer(data)
            elif message_type == 'answer':
                await self.handle_answer(data)
            elif message_type == 'ice_candidate':
                await self.handle_ice_candidate(data)
            elif message_type == 'join_room':
                await self.handle_join_room(data)
            elif message_type == 'code_change':
                await self.handle_code_change(data)
            elif message_type == 'cursor_position':
                await self.handle_cursor_position(data)
            elif message_type == 'whiteboard_draw':
                await self.handle_whiteboard_draw(data)
            elif message_type == 'whiteboard_clear':
                await self.handle_whiteboard_clear(data)
            elif message_type == 'chat_message':
                await self.handle_chat_message(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
        
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
    
    # Mode Handlers
    
    async def handle_code_change(self, data):
        """Handle code editor changes"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'code_update',
                'code': data.get('code'),
                'language': data.get('language'),
                'from_user': self.user.username if self.user.is_authenticated else 'Anonymous',
                'from_channel': self.channel_name
            }
        )

    async def handle_cursor_position(self, data):
        """Handle execution cursor position"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_update',
                'position': data.get('position'),
                'from_user': self.user.username if self.user.is_authenticated else 'Anonymous',
                'from_channel': self.channel_name
            }
        )

    async def handle_whiteboard_draw(self, data):
        """Handle whiteboard drawing events"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'draw_event',
                'draw_data': data.get('draw_data'),
                'from_channel': self.channel_name
            }
        )

    async def handle_whiteboard_clear(self, data):
        """Handle whiteboard clear event"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'clear_board_event',
                'from_channel': self.channel_name
            }
        )

    async def handle_chat_message(self, data):
        """Handle chat messages"""
        # Save to DB if needed, for now just broadcast
        message = data.get('message')
        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_chat_message',
                    'message': message,
                    'username': self.user.username if self.user.is_authenticated else 'Anonymous',
                    'timestamp': 'Just now'  # You can format actual time
                }
            )

    # WebRTC Handlers (Existing)
    
    async def handle_offer(self, data):
        """Handle WebRTC offer"""
        target_user = data.get('target')
        offer = data.get('offer')
        
        # Send offer to target user
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_offer',
                'offer': offer,
                'from_user': self.user.username if self.user.is_authenticated else 'Anonymous',
                'from_channel': self.channel_name,
                'target': target_user
            }
        )
        
        logger.info(f"Offer sent from {self.user.username if self.user.is_authenticated else 'Anonymous'} to {target_user}")
    
    async def handle_answer(self, data):
        """Handle WebRTC answer"""
        target_channel = data.get('target_channel')
        answer = data.get('answer')
        
        # Send answer to specific channel
        await self.channel_layer.send(
            target_channel,
            {
                'type': 'webrtc_answer',
                'answer': answer,
                'from_user': self.user.username if self.user.is_authenticated else 'Anonymous',
                'from_channel': self.channel_name
            }
        )
        
        logger.info(f"Answer sent from {self.user.username if self.user.is_authenticated else 'Anonymous'}")
    
    async def handle_ice_candidate(self, data):
        """Handle ICE candidate"""
        target_channel = data.get('target_channel')
        candidate = data.get('candidate')
        
        # Send ICE candidate to specific channel
        if target_channel:
            await self.channel_layer.send(
                target_channel,
                {
                    'type': 'ice_candidate',
                    'candidate': candidate,
                    'from_user': self.user.username if self.user.is_authenticated else 'Anonymous',
                    'from_channel': self.channel_name
                }
            )
        else:
            # Broadcast to all in room (for group calls)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'ice_candidate',
                    'candidate': candidate,
                    'from_user': self.user.username if self.user.is_authenticated else 'Anonymous',
                    'from_channel': self.channel_name
                }
            )
        
        logger.debug(f"ICE candidate sent from {self.user.username if self.user.is_authenticated else 'Anonymous'}")
    
    async def handle_join_room(self, data):
        """Handle explicit room join request"""
        # Send list of current users in room
        await self.send(text_data=json.dumps({
            'type': 'room_users',
            'message': 'Joined room successfully'
        }))
    
    # Channel Layer Event Handlers
    
    async def code_update(self, event):
        """Broadcast code updates"""
        if event['from_channel'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'code_update',
                'code': event['code'],
                'language': event.get('language'),
                'from_user': event['from_user']
            }))

    async def cursor_update(self, event):
        """Broadcast cursor updates"""
        if event['from_channel'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'cursor_update',
                'position': event['position'],
                'from_user': event['from_user']
            }))

    async def draw_event(self, event):
        """Broadcast drawing events"""
        if event['from_channel'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'draw_event',
                'draw_data': event['draw_data']
            }))

    async def clear_board_event(self, event):
        """Broadcast clear board event"""
        if event['from_channel'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'clear_board_event'
            }))

    async def new_chat_message(self, event):
        """Broadcast chat messages"""
        await self.send(text_data=json.dumps({
            'type': 'new_chat_message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    async def user_joined(self, event):
        """Send user joined notification"""
        # Don't send to self
        if event['channel_name'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'username': event['username'],
                'channel_name': event['channel_name']
            }))
    
    async def user_left(self, event):
        """Send user left notification"""
        # Don't send to self
        if event['channel_name'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id'],
                'username': event['username'],
                'channel_name': event['channel_name']
            }))
    
    async def webrtc_offer(self, event):
        """Forward WebRTC offer"""
        # Only send to target user or broadcast if no specific target
        target = event.get('target')
        if not target or target == (self.user.username if self.user.is_authenticated else 'Anonymous'):
            await self.send(text_data=json.dumps({
                'type': 'offer',
                'offer': event['offer'],
                'from_user': event['from_user'],
                'from_channel': event['from_channel']
            }))
    
    async def webrtc_answer(self, event):
        """Forward WebRTC answer"""
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'answer': event['answer'],
            'from_user': event['from_user'],
            'from_channel': event['from_channel']
        }))
    
    async def ice_candidate(self, event):
        """Forward ICE candidate"""
        # Don't send to self
        if event['from_channel'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'ice_candidate',
                'candidate': event['candidate'],
                'from_user': event['from_user'],
                'from_channel': event['from_channel']
            }))

