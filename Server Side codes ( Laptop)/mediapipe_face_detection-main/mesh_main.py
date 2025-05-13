import cv2
import mediapipe as mp
import socket
import time

# MediaPipe setup
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# Simulated servo range (for horizontal and vertical movement)
X_MIN = 0
X_MAX = 180
Y_MIN = 0
Y_MAX = 180

# Connect to Raspberry Pi server
SERVER_IP = '192.168.168.195'  # Replace with Raspberry Pi IP
PORT = 5050
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))
print(f"[CLIENT] Connected to server at {SERVER_IP}:{PORT}")

cap = cv2.VideoCapture(0)

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Convert the BGR image to RGB
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image_rgb)

        # Convert back to BGR for OpenCV
        image.flags.writeable = True
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        # Process detected face
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Extract nose tip landmark (landmark #1 is typically nose tip)
                nose = face_landmarks.landmark[1]
                image_height, image_width, _ = image.shape
                nose_x = int(nose.x * image_width)
                nose_y = int(nose.y * image_height)

                # Convert face position to simulated servo angles
                servo_x = max(X_MIN, min(X_MAX, 180 - int((nose_x / image_width) * 180)))
                servo_y = max(Y_MIN, min(Y_MAX, int((nose_y / image_height) * 180)))

                # Send angles to Raspberry Pi server
                data = f"{servo_x},{servo_y}"
                client_socket.sendall(data.encode('utf-8'))
                print(f"[CLIENT] Sent Angles -> Servo X: {servo_x}, Servo Y: {servo_y}")

                # Optional: draw face mesh
                mp_drawing.draw_landmarks(
                    image=image_bgr,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION)

        # Show image
        cv2.imshow('Face Tracking Simulation', cv2.flip(image_bgr, 1))
        if cv2.waitKey(5) & 0xFF == 27:  # Press Esc to exit
            break

cap.release()
cv2.destroyAllWindows()
client_socket.close()
