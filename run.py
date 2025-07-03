import time
import pynput.mouse as mouse
import pynput.keyboard as keyboard
import sys
import math

class EventReplayer:
    def __init__(self):
        self.stop_replay = False
        self.mouse_controller = mouse.Controller()
        self.keyboard_listener = None
    
    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.stop_replay = True
            return False
    
    def start_keyboard_listener(self):
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.keyboard_listener.start()
    
    def stop_keyboard_listener(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
    
    def load_events(self, file_path):
        events = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    event = eval(line.strip())
                    if event[0] == 'divider':
                        continue
                    events.append(event)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error loading {file_path}: {e}")
            return None
        return events
    
    def auto_click(self, time_diff):
        """Handle possible popups by auto-clicking to dismiss"""
        for _ in range(math.ceil(time_diff / 3) + 1):
            if self.stop_replay:
                sys.exit(0)
            
            # Click at specific position to dismiss popups
            popup_position = (317, 137)
            self.mouse_controller.position = popup_position
            self.mouse_controller.click(mouse.Button.left)
            time.sleep(3)
    
    def execute_click_event(self, x, y, details):
        button_name, pressed = details
        self.mouse_controller.position = (x, y)
        
        button = getattr(mouse.Button, button_name)
        if pressed:
            self.mouse_controller.press(button)
        else:
            self.mouse_controller.release(button)
    
    def execute_scroll_event(self, x, y, details):
        dx, dy = details
        self.mouse_controller.position = (x, y)
        self.mouse_controller.scroll(dx, dy)
    
    def replay_single_file(self, file_path, events, repetitions):
        for i in range(repetitions):
            if self.stop_replay:
                sys.exit(0)
                
            print(f'Starting replay {i+1} of {file_path}')
            
            for event in events:
                if self.stop_replay:
                    sys.exit(0)
                
                event_type, x, y, *details, time_diff = event
                
                # Handle possible popups during autoplay
                if time_diff > 60:
                    self.auto_click(time_diff)
                else:
                    time.sleep(time_diff)
                
                # Execute the event
                if event_type == 'click':
                    self.execute_click_event(x, y, details)
                elif event_type == 'scroll':
                    self.execute_scroll_event(x, y, details)
            
            time.sleep(2)  # Pause between repetitions
    
    def replay_events(self, replay_configs):
        self.start_keyboard_listener()
        
        try: 
            for file_name, repetitions in replay_configs:
                if self.stop_replay:
                    sys.exit(0)
               
                file_path = f'./runs/{file_name}.txt'
                events = self.load_events(file_path)
                
                if events is None:
                    continue
                
                self.replay_single_file(file_path, events, repetitions)
                time.sleep(5)  # Pause between files
        
        finally:
            self.stop_keyboard_listener()

def parse_command_line_args():
    """Parse command line arguments into file-count pairs"""
    file_names = sys.argv[1:]
    
    if len(file_names) % 2 != 0:
        print("Error: Please provide pairs of file names and replay counts.")
        print("Usage: python run.py replay1.txt 3 replay2.txt 2")
        sys.exit(1)
    
    replay_configs = []
    try:
        for i in range(0, len(file_names), 2):
            file_name = file_names[i]
            count = int(file_names[i + 1])
            replay_configs.append((file_name, count))
    except ValueError:
        print("Error: Replay counts must be integers.")
        sys.exit(1)
    
    return replay_configs

def main():
    replay_configs = parse_command_line_args()
    
    replayer = EventReplayer()
    replayer.replay_events(replay_configs)

if __name__ == "__main__":
    main()