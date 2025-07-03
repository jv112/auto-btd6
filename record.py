import pynput.mouse as mouse
import pynput.keyboard as keyboard
import time
import os

class EventRecorder:
    def __init__(self, replay_name):
        self.events = []
        self.last_event_time = None
        self.pause = False
        self.path = f'./runs/{replay_name}.txt'
    
    def on_click(self, x, y, button, pressed):
        if self.pause:
            return
        event_time = time.time()
        time_diff = event_time - self.last_event_time if self.last_event_time else 0
        self.events.append(('click', x, y, button.name, pressed, time_diff))
        self.last_event_time = event_time
        print('click', x, y, button.name, pressed, time_diff)

    def on_scroll(self, x, y, dx, dy):
        if self.pause:
            return
        event_time = time.time()
        time_diff = event_time - self.last_event_time if self.last_event_time else 0
        self.events.append(('scroll', x, y, dx, dy, time_diff))
        self.last_event_time = event_time
        print('scroll', x, y, dx, dy, time_diff)

    def on_press(self, key):
        if key == keyboard.Key.f1:
            return False
        if key == keyboard.Key.f2:
            self.pause = not self.pause
            if self.pause:
                print("Recording paused. Press F2 to resume.")
            else:
                print("Recording resumed.")
        if key == keyboard.Key.f3:
            print("Writing divider to file.")
            self.events.append(('divider', time.time()))
    
    def save_events(self):
        with open(self.path, 'w') as f:
            for event in self.events:
                f.write(f"{event}\n")

if __name__ == "__main__":
    if not os.path.exists('runs'):
        os.makedirs('runs')

    replay_name = input("Enter the name of the replay file: ").strip()
    
    recorder = EventRecorder(replay_name)

    print("Click or scroll the mouse to record events.")
    print("Press F1 to stop recording, F2 to pause/resume, and F3 to write a divider.")

    mouse_listener = mouse.Listener(on_click=recorder.on_click, on_scroll=recorder.on_scroll)
    mouse_listener.start()

    keyboard_listener = keyboard.Listener(on_press=recorder.on_press)
    keyboard_listener.start()

    keyboard_listener.join()

    recorder.save_events()
    print(f"Events saved to {recorder.path}.")