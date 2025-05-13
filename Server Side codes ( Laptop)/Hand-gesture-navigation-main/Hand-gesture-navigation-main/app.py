import cv2
import mediapipe as mp
import time
import socket
import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread

# ====== NETWORK CONFIG ======
PI_IP = "192.168.175.195"
PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)

# ====== VALID GESTURES ======
VALID_GESTURES = {
    (0, 0, 0, 0, 0): 'forward',
    (0, 1, 1, 0, 0): 'backward',
    (0, 1, 1, 1, 0): 'tank_left',
    (0, 1, 1, 1, 1): 'tank_right',
    (1, 1, 1, 1, 1): 'stop',
    (1, 0, 0, 0, 1): 'crab_right',
    (0, 1, 0, 0, 1): 'rotate_cw',
    (0, 1, 1, 0, 1): 'rotate_ccw',
    (0, 1, 0, 1, 0): 'fwd_left',
    (0, 1, 0, 1, 1): 'fwd_right',
    (0, 1, 1, 0, 0): 'bwd_left',
    (0, 1, 1, 0, 1): 'bwd_right',
    (1, 1, 0, 0, 0): 'soft_left',
    (1, 1, 1, 0, 0): 'soft_right'
}

# ====== MEDIA PIPE SETUP ======
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# ====== GUI SETUP ======
class GestureControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gesture Control GUI")
        self.connected = False
        self.prev_actions = [None, None]
        self.last_action_times = [0, 0]

        self.setup_gui()

    def setup_gui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        self.ip_var = tk.StringVar(value=PI_IP)
        ttk.Label(frame, text="Raspberry Pi IP:").grid(row=0, column=0, sticky='w')
        self.ip_entry = ttk.Entry(frame, textvariable=self.ip_var, width=20)
        self.ip_entry.grid(row=0, column=1)

        self.connect_btn = ttk.Button(frame, text="Connect", command=self.connect_to_pi)
        self.connect_btn.grid(row=0, column=2, padx=5)

        self.log_box = scrolledtext.ScrolledText(frame, width=60, height=10, state='disabled')
        self.log_box.grid(row=1, column=0, columnspan=3, pady=10)

        self.video_label = tk.Label(frame)
        self.video_label.grid(row=2, column=0, columnspan=3)

        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.update_video()

    def log(self, msg):
        self.log_box.configure(state='normal')
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.configure(state='disabled')
        self.log_box.yview(tk.END)

    def connect_to_pi(self):
        global PI_IP
        PI_IP = self.ip_var.get()
        self.log(f"[*] Trying to connect to Raspberry Pi at {PI_IP}...")
        try:
            sock.sendto("CONNECT_REQUEST".encode(), (PI_IP, PORT))
            data, _ = sock.recvfrom(1024)
            if data.decode().strip() == "CONNECTED":
                self.connected = True
                self.log("[+] Connected to Raspberry Pi.")
        except socket.timeout:
            self.log("[!] Connection timeout. Raspberry Pi did not respond.")

    def update_video(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    gesture = self.recognize_gesture(hand_landmarks)
                    if gesture and self.connected:
                        if gesture != self.prev_actions[i % 2] or time.time() - self.last_action_times[i % 2] > 1:
                            sock.sendto(gesture.encode(), (PI_IP, PORT))
                            self.log(f"[>] Sent gesture from Hand {i+1}: {gesture}")
                            self.prev_actions[i % 2] = gesture
                            self.last_action_times[i % 2] = time.time()

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 480))
            photo = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            img = cv2.imencode('.png', photo)[1].tobytes()
            photo_image = tk.PhotoImage(data=img)
            self.video_label.configure(image=photo_image)
            self.video_label.image = photo_image

        self.root.after(10, self.update_video)

    def recognize_gesture(self, hand_landmarks):
        tips_ids = [4, 8, 12, 16, 20]
        fingers = [0] * 5
        fingers[0] = 1 if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x else 0
        for i in range(1, 5):
            fingers[i] = 1 if hand_landmarks.landmark[tips_ids[i]].y < hand_landmarks.landmark[tips_ids[i]-2].y else 0
        return VALID_GESTURES.get(tuple(fingers), None)

    def on_close(self):
        self.running = False
        self.cap.release()
        self.root.destroy()
        sock.close()


if __name__ == '__main__':
    root = tk.Tk()
    app = GestureControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
