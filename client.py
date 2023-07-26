import cv2
import numpy as np
import socket
import struct
import time # Jiaxi
from io import BytesIO

# Capture frame
cap = cv2.VideoCapture(1)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.0.128', 8080))

while cap.isOpened():
    _, frame = cap.read()

    memfile = BytesIO()
    np.save(memfile, frame)
    memfile.seek(0)
    data = memfile.read()

    # Send form byte array: frame size + frame content
    client_socket.sendall(struct.pack("Ld", len(data), time.time()) + data) # Jiaxi

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
