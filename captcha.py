import random
import string
import io
import hashlib
import time
from PIL import Image, ImageDraw, ImageFont

CAPTCHA_EXPIRE_SECONDS = 300

captcha_store = {}


class CaptchaManager:
    @staticmethod
    def generate_captcha_text(length=4):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    @staticmethod
    def generate_captcha_image(text):
        width, height = 120, 40
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            except:
                font = ImageFont.load_default()
        
        for i, char in enumerate(text):
            x = 15 + i * 25
            y = random.randint(5, 10)
            color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
            draw.text((x, y), char, font=font, fill=color)
        
        for _ in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            color = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
        
        for _ in range(50):
            x = random.randint(0, width)
            y = random.randint(0, height)
            color = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
            draw.point((x, y), fill=color)
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    
    @staticmethod
    def generate_captcha_key():
        return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()
    
    @staticmethod
    def store_captcha(key: str, text: str):
        captcha_store[key] = {
            'text': text.upper(),
            'expire_at': time.time() + CAPTCHA_EXPIRE_SECONDS
        }
        CaptchaManager.cleanup_expired()
    
    @staticmethod
    def verify_captcha(key: str, user_input: str) -> bool:
        if key not in captcha_store:
            return False
        
        stored = captcha_store[key]
        
        if time.time() > stored['expire_at']:
            del captcha_store[key]
            return False
        
        is_valid = stored['text'] == user_input.upper()
        
        if is_valid:
            del captcha_store[key]
        
        return is_valid
    
    @staticmethod
    def cleanup_expired():
        current_time = time.time()
        expired_keys = [k for k, v in captcha_store.items() if v['expire_at'] < current_time]
        for key in expired_keys:
            del captcha_store[key]
