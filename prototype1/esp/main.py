import network
import urequests as requests
import ujson
import socket
import time
from machine import Timer
import datetime


WIFI_SSID = "NokiaG42"
WIFI_PASSWORD = "tetra1234"
FLASK_SERVER_URL = "http://192.168.188.186:5000/data"                                        # config
ESP_PORT = 8080
ESP_ID = "ESP32_1" 
ANOTHER_ESP_URL = "http://192.168.188.123:8080/data"  

is_routed = False                                                                       # variable for use with 2 esp when routhing data through another esp

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    print("Connecting to WiFi...")
    while not wlan.isconnected():
        time.sleep(1)
    print("Connected to WiFi:", wlan.ifconfig())


def send_data_to_server(server_url, data):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(server_url, headers=headers, data=ujson.dumps(data))
        print(f"Sent data to {server_url}, response:", response.text)
        return True
    except Exception as e:
        print(f"Failed to send data to {server_url}: {e}")
        return False

def create_payload():
    current_time = datetime.datetime.now()
    return {"id": ESP_ID, "routed": is_routed,time:current_time}

def handle_client(client):                                                                            # incoming http requests for routing
    global is_routed
    try:
        request = client.recv(1024).decode('utf-8')
        if "POST /data" in request:
            body_start = request.find("\r\n\r\n") + 4           
            body = request[body_start:]
            data = ujson.loads(body)
            print("Received data:", data)                                                             # extract json data from the request body

           
            if not send_data_to_server(FLASK_SERVER_URL, data):
                print("Failed to forward data to Flask server.")                                        # forward data to the flask server
            

            client.send('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n')
            client.send(ujson.dumps({"status": "success"}))                                             # send response back to the client
        else:
    
            client.send('HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n')
            client.send('Not Found')
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client.close()

def start_server():                                                                                    # Start HTTP server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', ESP_PORT))
    server_socket.listen(5)
    print(f"Server running on port {ESP_PORT}...")

    while True:
        client, addr = server_socket.accept()
        print(f"Connection from {addr}")
        handle_client(client)

def send_periodic_data(timer):
    global is_routed
    payload = create_payload()


    if not send_data_to_server(FLASK_SERVER_URL, payload):
        print("Flask server not reachable, attempting to send to another ESP32...")                     # attempt to send to the Flask server

        # Send to another ESP32
        is_routed = True
        if not send_data_to_server(ANOTHER_ESP_URL, payload):
            print("Failed to send data to another ESP32.")
        is_routed = False


def main():
    connect_wifi()

    timer = Timer(-1)
    timer.init(period=5000, mode=Timer.PERIODIC, callback=send_periodic_data)

    start_server()

if __name__ == '__main__':
    main()
