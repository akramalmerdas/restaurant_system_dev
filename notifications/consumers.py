from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OrderNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the admin_notifications group
        await self.channel_layer.group_add(
            "admin_notifications",
            self.channel_name
        )
        await self.accept()
        
        # Send a connection confirmation message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to order notification system'
        }))

    async def disconnect(self, close_code):
        # Leave the admin_notifications group
        await self.channel_layer.group_discard(
            "admin_notifications",
            self.channel_name
        )

    # Receive message from WebSocket (from client)
    async def receive(self, text_data):
        # We don't need to handle incoming messages for this notification system
        pass

    # Receive message from admin_notifications group
    async def order_notification(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'order_id': event['order_id'],
            'customer': event['customer'],
            'total': event['total'],
            'timestamp': event['timestamp']
        }))