from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def service_gmail():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # if os.path.exists('credentials.json'):
    #     with open('token.pickle', 'rb') as token:
    #         creds = pickle.load(token)
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    flow = InstalledAppFlow.from_client_secrets_file('/home/pain/Desktop/camb_ai/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # # Save the credentials for the next run
        # with open('token.pickle', 'wb') as token:
        #     pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service



from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64

def send_email(service, sender, to, subject, body_text, file_path=None):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(body_text)
    message.attach(msg)

    if file_path:
        attachment = MIMEBase('application', 'octet-stream')
        with open(file_path, 'rb') as file:
            attachment.set_payload(file.read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
        message.attach(attachment)

    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    message = service.users().messages().send(userId='me', body=body).execute()
    # print('Message Id: %s' sent % message['id'])
    return message

##########################33
import requests
import os

def download_video(url, save_path):
    try:
        # Send a GET request to the URL to get the video content
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open a file in binary write mode to save the video
            with open(save_path, 'wb') as file:
                # Write the content of the response to the file
                file.write(response.content)
            print("Video downloaded successfully!")
            return save_path
        else:
            print(f"Failed to download video. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


########################################################
import gradio as gr
import requests
import time 
import os 

os.environ["GRADIO_TEMP_DIR"] = "/home/pain/Desktop/camb_ai"


def process_video(video_file):

    url = "https://client.camb.ai/apis/end_to_end_dubbing"

    print("video_file:", video_file)
    
    payload = {
        "video_url": "{video_file}",
        "source_language": 1,
        "target_language": 4
    }

    headers = {
        "x-api-key": "c3a0446d-4c60-4c55-a9ed-26c1f2424e2b",
        "Content-Type": "application/json"
    }

    task_id = None

    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        task_id = data.get("task_id")
        if task_id:
            print("Task ID:", task_id)
        else:
            print("Task ID not found in response.")
    else:
        print("Request failed with status code:", response.status_code)
        print("Response:", response.text)

    # change this when you find a way to upload local video 
    return "660945d2-6a54-4b8b-8295-aa08f3d432d7"


def check_task_status_and_get_video_url(task_id_in):
    url_status = f"https://client.camb.ai/apis/end_to_end_dubbing/{task_id_in}"
    url_dubbed_run_info = "https://client.camb.ai/apis/dubbed_run_info/"

    headers = {
        "x-api-key": "c3a0446d-4c60-4c55-a9ed-26c1f2424e2b",
        "Content-Type": "application/json"
    }

    video_url = None
    audio_url = None

    while True:
        response = requests.request("GET", url_status, headers=headers)

        print("Inside the while looop: ", response)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            print("status:" , status)
            # Edit this to check for the status you want status
            if status == "SUCCESS":
                print("Task completed successfully!")
                run_id = data.get("run_id")
                print("Run ID:", run_id)
                if run_id:
                    dubbed_run_info_url = url_dubbed_run_info + str(run_id)
                    dubbed_run_info_response = requests.get(dubbed_run_info_url, headers=headers)
                    if dubbed_run_info_response.status_code == 200:
                        print("Dubbed run info:")
                        print(dubbed_run_info_response.text)
                        data = dubbed_run_info_response.json()
                        video_url = data.get("video_url")
                        audio_url = data.get("audio_url")
                        print("Video URL:", video_url)
                        print("Audio URL:", audio_url)
                    else:
                        print("Failed to fetch dubbed run info. Status code:", dubbed_run_info_response.status_code)
                else:
                    print("Run ID not found in task status response.")
                return video_url
            elif status == "PENDING":
                print("Task is still pending...")
            else:
                print(f"Task failed with status: {status}")
                break
        else:
            print("Failed to fetch task status. Status code:", response.status_code)
            break

        time.sleep(10)  # Wait for 5 seconds before checking again
        
    return video_url
        

def predict(video_input):

    # print(video_input)

    task_id_out = process_video(video_input)

    print("task_id_out:", task_id_out)

    video_url = check_task_status_and_get_video_url(task_id_out)

    print("video_url:", video_url)



    # send the video to the email

    # Download the video 

    # Example usage
    video_url = f"{video_url}"
    save_path = "output_video.mkv"  # Change this to the desired save path
    downloaded_path = download_video(video_url, save_path)
    print("Downloaded video path:", downloaded_path)

    # Get the video path localy 


    # Example usage
    service = service_gmail()
    send_email(service, 'albarham.muhammad@gmail.com', 'mohammedbrham98@gmail.com', 'Video from camb ai v2', 'Hello, this is the body.', 'input.mp4')

    print("The email is already sent")
    return video_url

# Araclip demo 
with gr.Blocks() as demo_araclip:

    # gr.Markdown("## Choose the dataset")

    # dadtaset_select = gr.Radio(["XTD dataset", "Flicker 8k dataset"], value="XTD dataset", label="Dataset", info="Which dataset you would like to search in?")

    gr.Markdown("## Input parameters")
    
    txt = gr.Textbox(label="Email Address")

    video_input = gr.Video()
    video_output = gr.Video()

    # print(video_input)

    with gr.Row():
        btn = gr.Button("Send an email", scale=1)

    btn.click(predict, inputs=[video_input], outputs=[video_output])


# Group the demos in a TabbedInterface 
with gr.Blocks() as demo:

    gr.Markdown("<font color=red size=10><center>Removing the language barries as Ferari Speed</center></font>")

    gr.TabbedInterface([demo_araclip], ["Our Model"])


if __name__ == "__main__":
    
    demo.launch()