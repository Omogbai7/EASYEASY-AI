import os
import requests
from typing import Optional, Dict, Any

class WhatsAppService:
    def __init__(self):
        self.api_token = os.getenv('WHATSAPP_API_TOKEN')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def send_text_message(self, to: str, message: str) -> Dict[str, Any]:
        """Send a text message to a WhatsApp user"""
        url = f"{self.base_url}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            print(f"Error sending message: {e}")
            return {"success": False, "error": str(e)}

    def send_image_message(self, to: str, image_url_or_id: str, caption: str = "") -> Dict[str, Any]:
        """Send an image (supports both URL and Media ID)"""
        url = f"{self.base_url}/messages"
        
        # Determine if it's a Link (http) or an ID (numbers)
        image_obj = {}
        if image_url_or_id.startswith("http"):
            image_obj = {"link": image_url_or_id, "caption": caption}
        else:
            image_obj = {"id": image_url_or_id, "caption": caption}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "image",
            "image": image_obj
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            print(f"Error sending image: {e}")
            return {"success": False, "error": str(e)}

    def send_video_message(self, to: str, video_url_or_id: str, caption: str = "") -> Dict[str, Any]:
        """Send a video (supports both URL and Media ID)"""
        url = f"{self.base_url}/messages"
        
        video_obj = {}
        if video_url_or_id.startswith("http"):
            video_obj = {"link": video_url_or_id, "caption": caption}
        else:
            video_obj = {"id": video_url_or_id, "caption": caption}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "video",
            "video": video_obj
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            print(f"Error sending video: {e}")
            return {"success": False, "error": str(e)}

    def send_button_message(self, to: str, body_text: str, buttons: list, button_ids: list = None) -> Dict[str, Any]:
        """Send an interactive button message"""
        url = f"{self.base_url}/messages"

        button_components = []
        for idx, button_text in enumerate(buttons[:3]):
            # Use custom ID if provided, otherwise default to btn_0, btn_1
            b_id = button_ids[idx] if button_ids and idx < len(button_ids) else f"btn_{idx}"
            
            button_components.append({
                "type": "reply",
                "reply": {
                    "id": b_id, 
                    "title": button_text[:20]
                }
            })

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body_text
                },
                "action": {
                    "buttons": button_components
                }
            }
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            print(f"Error sending button message: {e}")
            return {"success": False, "error": str(e)}

    def send_list_message(self, to: str, body_text: str, button_text: str, sections: list) -> Dict[str, Any]:
        """Send an interactive list message"""
        url = f"{self.base_url}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body_text
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            print(f"Error sending list message: {e}")
            return {"success": False, "error": str(e)}

    def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as read"""
        url = f"{self.base_url}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {"success": True}
        except Exception as e:
            print(f"Error marking message as read: {e}")
            return {"success": False, "error": str(e)}
