import logging
import sys
import os
from threading import Thread
from playsound import playsound
import time

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Clear handlers if any exist
if root_logger.handlers:
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

# Create file handler
file_handler = logging.FileHandler('logs/app_debug.log', mode='w', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Add handlers to root logger
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Force an immediate log flush
root_logger.debug('Application starting...')
file_handler.flush()
console_handler.flush()

# Use direct print statements as backup
print("DIRECT PRINT: Application starting...")

class DesktopApp:
    def __init__(self):
        self.sound_file = os.path.join(os.path.dirname(__file__), 'static', 'sounds', 'notification.wav')
        self.sound_thread = None
        self.stop_sound = False
        logging.debug(f'Sound file path: {self.sound_file}')
        print(f"DIRECT PRINT: Sound file path: {self.sound_file}")

    def play_sound(self):
        logging.debug('Starting sound playback loop')
        print("DIRECT PRINT: Starting sound playback loop")
        while not self.stop_sound:
            try:
                logging.debug('Playing sound file')
                print("DIRECT PRINT: Playing sound file")
                playsound(self.sound_file)
                logging.debug('Sound playback completed')
                print("DIRECT PRINT: Sound playback completed")
            except Exception as e:
                error_msg = f"Error playing sound: {e}"
                logging.error(error_msg)
                print(f"DIRECT PRINT ERROR: {error_msg}")
                break

    def start_sound(self):
        logging.debug('start_sound called from JavaScript')
        print("DIRECT PRINT: start_sound called from JavaScript")
        self.stop_sound = False
        self.sound_thread = Thread(target=self.play_sound)
        self.sound_thread.daemon = True
        self.sound_thread.start()
        logging.debug(f'Sound thread started: {self.sound_thread.name}')
        print(f"DIRECT PRINT: Sound thread started: {self.sound_thread.name}")
        return True

    def stop_sound_playback(self):
        logging.debug('stop_sound_playback called from JavaScript')
        print("DIRECT PRINT: stop_sound_playback called from JavaScript")
        self.stop_sound = True
        if self.sound_thread:
            logging.debug(f'Waiting for sound thread to join: {self.sound_thread.name}')
            print(f"DIRECT PRINT: Waiting for sound thread to join: {self.sound_thread.name}")
            self.sound_thread.join(timeout=2.0)
            logging.debug('Sound thread stopped')
            print("DIRECT PRINT: Sound thread stopped")
        return True

if __name__ == '__main__':
    try:
        logging.debug('Creating DesktopApp instance')
        print("DIRECT PRINT: Creating DesktopApp instance")
        app = DesktopApp()
        
        logging.debug('Creating PyWebView window')
        print("DIRECT PRINT: Creating PyWebView window")
        import webview
        window = webview.create_window('Mocha Cafe', 'http://localhost:8000', width=1200, height=800 )
        
        logging.debug('Exposing Python methods to JavaScript')
        print("DIRECT PRINT: Exposing Python methods to JavaScript")
        window.expose(app.start_sound, app.stop_sound_playback)
        
        logging.debug('Starting PyWebView')
        print("DIRECT PRINT: Starting PyWebView")
        webview.start(debug=True)
        logging.debug('PyWebView terminated')
        print("DIRECT PRINT: PyWebView terminated")
    except Exception as e:
        logging.exception(f"Unhandled exception: {e}")
        print(f"DIRECT PRINT CRITICAL ERROR: {e}")
