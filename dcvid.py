import json
import uuid
import requests
from flask import Flask, redirect, request, render_template, jsonify, session, url_for
from moviepy import VideoFileClip
import os
from libares import jsonreturn
import traceback 
#For generating unique IDs if needed
data =0
app = Flask(__name__)
app.secret_key = os.urandom(24)  
ID_URL_MAP_FILE = "id_url_map.json" #Name of JSON file for storing mappings.
user_upload_status = {}
def load_id_url_map():
  """Loads the ID-URL map from the JSON file. Creates it if it doesn't exist."""
  try:
    with open(ID_URL_MAP_FILE, "r") as f:
      return json.load(f)
  except FileNotFoundError:
    return {}

def save_id_url_map(id_url_map):
  """Saves the ID-URL map to the JSON file."""
  with open(ID_URL_MAP_FILE, "w") as f:
    json.dump(id_url_map, f, indent=2)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:  # Check if user is logged in
        user_id = str(uuid.uuid4())#
        session['user_id'] = user_id   
    
    user_id = session['user_id']
    if user_id in user_upload_status and user_upload_status[user_id] == "uploaded":
        return render_template('upload.html', error_message="You've already uploaded a video.  Please wait.")

    # ... (Rest of your upload processing code)
    file = request.files['mp4_file']
    unique_id = request.form.get('unique_id')
    id_url_map = load_id_url_map()
    if unique_id in id_url_map:
        return render_template('upload.html', error_message=f"Error: Unique ID '{unique_id}' already exists.")

    temp_filepath = os.path.join("temp", file.filename)
    os.makedirs("temp", exist_ok=True)
    file.save(temp_filepath)

    webhook_url = "https://discord.com/api/webhooks/1309979145434038343/RA26u6O4k3PeVQC2cFqp6gKbe3VfJmAt03VL4_whOQKP3ufktiaUav3Rx8as1zY3XMpH"


    try:
      clip = VideoFileClip(temp_filepath)
      compressed_filepath = os.path.join("temp", "compressed_" + file.filename)
      clip.write_videofile(compressed_filepath, codec="libx264", bitrate="750k", audio_bitrate="64k", audio_codec="aac")
      clip.close() 
      try:
          last_message_id = None

          # 1. Get Webhook Info to extract channel ID:
          response = requests.get(webhook_url)
          response.raise_for_status()
          webhook_info = response.json()
          channel_id = webhook_info['channel_id']  # Extract the channel ID

          # 2. Build CORRECT URL for channel messages using the channel_id
          channel_messages_url = f"https://discord.com/api/channels/{channel_id}/messages?limit=100"

          bot_token = "DISCORD_VIDEO_TOKEN"  # Store your bot token securely, don't hardcode!
          headers = {"Authorization": f"Bot {bot_token}"}


          response = requests.get(channel_messages_url, headers=headers)  # headers in the correct place
          response.raise_for_status()
          messages = response.json()
          if messages:
              last_message_id = messages[0]['id']
          else:
              print("No messages found in the channel")

      except requests.exceptions.RequestException as e:
          print(f"Error getting last message ID: {e}")
          return render_template('upload.html', error_message=f"Error getting last message ID: {e}")
      payload = {
            'content': f"Unique ID: {unique_id} \n .",
            'embeds': [],
        }
      if last_message_id: # if the last message id exists then add reference to it in the payload 
          payload['message_reference'] = {'message_id': last_message_id}

      with open(compressed_filepath, 'rb') as compressed_file:
           
             files = {'file': (file.filename, compressed_file.read())}
             response = requests.post(webhook_url, files=files, data=payload) # Include payload here



      if response.status_code  == 200:
          try:
              global data 
              data = response.json()
              message_url = jsonreturn.extract_url_from_discord_json(data)
              print(data)
              
              # Store the ID-URL mapping
              id_url_map = load_id_url_map()
              id_url_map[unique_id] = message_url
              save_id_url_map(id_url_map)
              user_upload_status[user_id] = "uploaded"
              return render_template('upload.html', discord_url=message_url)
          
          except json.JSONDecodeError as e:
              return render_template('upload.html', error_message=f"Error decoding Discord response: {e}")
          except Exception as e:
              return render_template('upload.html', error_message=f"Error processing Discord response: {e}")
      else:
          return render_template('upload.html', error_message=f"Error uploading to Discord: {response.status_code}, {response.content}")
    except Exception as e:
        print(f"Error during compression or upload: {e}")
        print(f"Traceback: {traceback.format_exc()}")  # Print the full traceback
        return render_template('upload.html', error_message=f"Error during compression or upload: {e} {traceback.format_exc()}") # Show in the template as well
    finally:
        os.remove(temp_filepath)
        if os.path.exists(compressed_filepath):
            os.remove(compressed_filepath)
        




@app.route('/get_url', methods=['POST'])
def get_url():
    unique_id = request.form.get('unique_id')
    id_url_map = load_id_url_map()
    url = id_url_map.get(unique_id)
    if url:
        return render_template('upload.html', url=url)  # Return the URL as JSON
    else:
        return render_template('upload.html', url=url) # Return an error if the ID isn't found
    



@app.route('/logout', methods=['GET'])
def logout():
    user_id = session.get('user_id')  # Get the user ID from the session
    if user_id and user_id in user_upload_status:
        del user_upload_status[user_id]  # Remove the user from the upload status dictionary
    session.pop('user_id', None)  # Clear the user's session
    return redirect(url_for('index'))  # Redirect to your home page

@app.route('/')
def index():
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)

