import cv2
import numpy as np
import socket
import struct
import time # Jiaxi
from io import BytesIO

# Capture frame
cap = cv2.VideoCapture(0)

# Frame width Jiaxi
FRAME_WIDTH = 1920

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8080))

while cap.isOpened():
    _, frame = cap.read()

    # Resize frame Jiaxi
    aspect_ratio = frame.shape[0] / frame.shape[1]
    frame = cv2.resize(frame, (FRAME_WIDTH, int(FRAME_WIDTH * aspect_ratio)))

    memfile = BytesIO()
    np.save(memfile, frame)
    memfile.seek(0)
    data = memfile.read()

    # Send form byte array: frame size + frame content
    client_socket.sendall(struct.pack("Ld", len(data), time.time()) + data) # Jiaxi

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
