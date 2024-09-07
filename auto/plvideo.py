import time
import uuid
import requests
import convert_to_requests
import os
import base64
import mimetypes

print("Step 1: go on https://studio.plvideo.ru and copy any request as curl")
req = convert_to_requests.curl_to_requests(input("Paste it here or empty to use request-plvideo.txt: ") or open('request-plvideo.txt').read())
print(req)

session = requests.Session()
session.headers = req.headers

print("Step 2: check account")
data = session.get("https://tokens.g2.plvideo.ru/v1/channels/").json()

print("Your channel is:", data['items'][0]['id'])
input("continue...")

video_path = input("Path to video: ")

print("Step 3: prepare to upload")

print("fetching video signature")
sign = session.post("https://upload.plvideo.ru/ru/files/sign/", json=
                    {
                        "channelId": data['items'][0]['id'],
                        "fileName": os.path.basename(video_path),
                        "fileSize": os.path.getsize(video_path),
                        "fileType": mimetypes.guess_type(video_path)[0]
                    }).json()
print(sign)
print("Video ID: ", sign['videoId'])
print("Sign: ", sign['sign'])

print("Allocating video ID")
session.post(f"https://studio-api.g1.plvideo.ru/v1/videos/{sign['videoId']}/create/").raise_for_status()

print("Step 4: upload video as single chunk (it may take a while)")

print("Getting path")
chunk_upl = session.post("https://upload.plvideo.ru/ru/files/", headers=
             {"X-Sign": sign['sign'],
              "Tus-Resumable": "1.0.0",
              "Upload-Offset": "0",
              "Upload-Concat": "partial",
              "Upload-Length": str(os.path.getsize(video_path))
              })

chunk_upl.raise_for_status()

print("Uploading to path", chunk_upl.headers['Location'])

with open(video_path, 'rb') as f:
    s = session.patch(chunk_upl.headers['Location'], data=f,
                 headers={"X-Sign": sign['sign'],
                          "Tus-Resumable": "1.0.0",
                          "Upload-Offset": "0",
                          "Upload-Concat": "partial",
                          "Content-Type": "application/offset+octet-stream",
                 })
    print("Response: ", s.status_code, s.text)
    s.raise_for_status()

print("Finalizing upload")
s = session.post("https://upload.plvideo.ru/ru/files/", headers=
             {"X-Sign": sign['sign'],
              "Tus-Resumable": "1.0.0",
              "Upload-Concat": "final;" + chunk_upl.headers['Location'],
              "Upload-Metadata": "filename " + base64.b64encode(os.path.basename(video_path).encode('utf-8')).decode('utf-8')
               + ",filetype " + base64.b64encode(mimetypes.guess_type(video_path)[0].encode('utf-8')).decode('utf-8')})
print("Response: ", s.status_code, s.text)
s.raise_for_status()

print("Step 5: finalize video metadata")

s = session.patch("https://studio-api.g1.plvideo.ru/v1/videos/" + sign['videoId'] + "/",
             json={
                 "cover": "blob:https://studio.plvideo.ru/" + str(uuid.uuid4()),
                 "visible": "link",
                 "playlistIds": [],
                 "tags": [],
                 "title": "test",
                 "description": "test"
             })
print("Response: ", s.status_code, s.text)
s.raise_for_status()

print("Step 6: wait for upload to be acknowledged")
while 1:
    s = session.get("https://studio-api.g1.plvideo.ru/v1/videos/" + sign['videoId'] + "/")
    print("Response: ", s.status_code, s.text)
    if s.json()['uploadStatus'] == 'success':
        print("Success!")
        break
    elif s.json()['uploadStatus'] == 'init':
        print("still waiting")
        time.sleep(1)
        continue
    else:
        raise Exception("unknown status: ", s.json()['uploadStatus'])

s = session.post("https://studio-api.g1.plvideo.ru/v1/videos/" + sign['videoId'] + "/publish/")
print("Response: ", s.status_code, s.text)
s.raise_for_status()

print("Done")