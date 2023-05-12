from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

token = os.getenv('FACEBOOK_TOKEN')


@app.route('/', methods=['GET', 'POST'])
def handle_webhook():

    if request.method == 'POST':
        data = request.get_json()
        # Print the data received from the webhook
        print(data)
        return jsonify({'status': 'success'})

    # Parse the challenge parameter from the request and return it as a JSON object
    challenge = request.args.get('hub.challenge')
    return jsonify({'challenge': challenge})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
