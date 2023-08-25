import cv2
import numpy
import socket
import struct
import threading
import time # Jiaxi
from io import BytesIO


class Streamer(threading.Thread):

    def __init__(self, hostname, port):
        threading.Thread.__init__(self)

        self.hostname = hostname
        self.port = port
        self.running = False
        self.streaming = False
        self.jpeg = None

    def run(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created')

        s.bind((self.hostname, self.port))
        print('Socket bind complete')

        payload_size = struct.calcsize("Ld")

        s.listen(10)
        print('Socket now listening')

        self.running = True

        while self.running:

            print('Start listening for connections...')

            conn, addr = s.accept()
            print("New connection accepted.")

            fps = 0
            last_fps_second = int(time.time())
            packet_delay_list = []
            frame_delay_list = []
            fps_list = []
            while True:

                data = conn.recv(payload_size)

                if data:
                    # Read frame size
                    msg_size = struct.unpack("Ld", data)[0]

                    # Read Sent Time # Jiaxi
                    sent_time = struct.unpack("Ld", data)[1]

                    # Calculat Packet Delay # Jiaxi
                    packet_delay = time.time() - sent_time
                    print("One-Way Packet Delay: " + str(packet_delay))
                    packet_delay_list.append(packet_delay)

                    # Read the payload (the actual frame)
                    data = b''
                    while len(data) < msg_size:
                        missing_data = conn.recv(msg_size - len(data))
                        if missing_data:
                            data += missing_data
                        else:
                            # Connection interrupted
                            self.streaming = False
                            break
                        
                    # Calculat Frame Delay # Jiaxi
                    frame_delay = time.time() - sent_time
                    print("One-Way Frame Delay: " + str(frame_delay))
                    frame_delay_list.append(frame_delay)
                    
                    # Skip building frame since streaming ended
                    if self.jpeg is not None and not self.streaming:
                        continue

                    # Convert the byte array to a 'jpeg' format
                    memfile = BytesIO()
                    memfile.write(data)
                    memfile.seek(0)
                    frame = numpy.load(memfile)

                    ret, jpeg = cv2.imencode('.jpg', frame)
                    self.jpeg = jpeg

                    # Calculate FPS # Jiaxi
                    curr_fps_second = int(time.time())
                    if curr_fps_second != last_fps_second:
                        print("FPS: " + str(fps))
                        fps_list.append(fps)
                        last_fps_second = curr_fps_second
                        fps = 0
                    fps += 1

                    self.streaming = True
                    
                else:
                    conn.close()
                    print('Closing connection...')
                    self.streaming = False
                    self.running = False
                    self.jpeg = None
                    break
        
        print("Average One-Way Packet Delay: " + str(numpy.average(numpy.array(packet_delay_list))))
        print("Average One-Way Frame Delay: " + str(numpy.average(numpy.array(frame_delay_list))))
        print("Average FPS: " + str(numpy.average(numpy.array(fps_list))))
        print('Exit thread.')

    def stop(self):
        self.running = False

    def get_jpeg(self):
        return self.jpeg.tobytes()
