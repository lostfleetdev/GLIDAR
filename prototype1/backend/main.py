from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

CSV_FILE_PATH = "data.csv"

# Function to write JSON data to a CSV file
def write_json_to_csv(data):
    # Check if the CSV file exists
    file_exists = os.path.isfile(CSV_FILE_PATH)
    
    with open(CSV_FILE_PATH, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        
        # Write header if the file is new
        if not file_exists:
            writer.writeheader()
        
        # Write the JSON data as a row in the CSV
        writer.writerow(data)


@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    print("Received data:", data)
    # return jsonify({"status": "success"}), 200 # simple data on sucess

    try:
        # Convert the JSON data to CSV
        write_json_to_csv(data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print("Error writing to CSV:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
