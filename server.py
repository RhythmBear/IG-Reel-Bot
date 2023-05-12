from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

token = os.getenv('FACEBOOK_TOKEN')


@app.route('/', methods=['POST'])
def handle_webhook():
    data = request.get_json()
    # Print the data received from the webhook
    print(data)
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
