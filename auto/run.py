import base64
import mimetypes
import os
import time
import uuid
import shutil

# Requires the `zip` command to be present

import convert_to_requests
import requests
lab_number = int(input("What is the lab number? "))
print("Step 1: make videos")

GH_REPO = "danya02/study_2024-2025_infosec"

RUTUBE_PLAYLIST_ID = "552121"
# https://rutube.ru/plst/552121

PLVIDEO_PLAYLIST_ID = "MVdb8FV3sHAh"

work = os.path.abspath(input("Path to work video: ").replace("'", ''))
present = os.path.abspath(input("Path to present video: ").replace("'", ''))

print("Step 2: upload videos to Plvideo")

print("2.1: go on https://studio.plvideo.ru and copy any request to 'studio-api.g1.plvideo.ru' as curl")
req = convert_to_requests.curl_to_requests(input("Paste it here or empty to use request-plvideo.txt: ") or open('request-plvideo.txt').read())
session = requests.Session()
session.headers = req.headers
try: del session.headers['Accept-Encoding']
except: pass

print("2.2: check account")
data = session.get("https://tokens.g2.plvideo.ru/v1/channels/").json()
print(data)
print("Your channel is:", data['items'][0]['id'])
input("continue...")

print("2.3: prepare to upload work")

print("fetching video signature")
sign = session.post("https://upload.plvideo.ru/ru/files/sign/", json=
                    {
                        "channelId": data['items'][0]['id'],
                        "fileName": os.path.basename(work),
                        "fileSize": os.path.getsize(work),
                        "fileType": mimetypes.guess_type(work)[0]
                    }).json()
print(sign)
print("Video ID: ", sign['videoId'])
print("Sign: ", sign['sign'])

print("Allocating video ID")
session.post(f"https://studio-api.g1.plvideo.ru/v1/videos/{sign['videoId']}/create/").raise_for_status()

print("2.4: upload video as single chunk (it may take a while)")

print("Getting path")
chunk_upl = session.post("https://upload.plvideo.ru/ru/files/", headers=
             {"X-Sign": sign['sign'],
              "Tus-Resumable": "1.0.0",
              "Upload-Offset": "0",
              "Upload-Concat": "partial",
              "Upload-Length": str(os.path.getsize(work))
              })

chunk_upl.raise_for_status()

print("Uploading to path", chunk_upl.headers['Location'])

with open(work, 'rb') as f:
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
              "Upload-Metadata": "filename " + base64.b64encode(os.path.basename(work).encode('utf-8')).decode('utf-8')
               + ",filetype " + base64.b64encode(mimetypes.guess_type(work)[0].encode('utf-8')).decode('utf-8')})
print("Response: ", s.status_code, s.text)
s.raise_for_status()

print("2.5: finalize video metadata")

s = session.patch("https://studio-api.g1.plvideo.ru/v1/videos/" + sign['videoId'] + "/",
             json={
                 "cover": "blob:https://studio.plvideo.ru/" + str(uuid.uuid4()),
                 "visible": "link",
                 "playlistIds": [PLVIDEO_PLAYLIST_ID],
                 "tags": [],
                 "title": "Лабораторная работа No" + str(lab_number) + " выполнение",
                 "description": ""
             })
print("Response: ", s.status_code, s.text)
s.raise_for_status()

print("2.6: wait for upload to be acknowledged")
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

plvideo_work_url = f'https://plvideo.ru/watch?v={sign["videoId"]}'


print("2.7: publish video")
s = session.post("https://studio-api.g1.plvideo.ru/v1/videos/" + sign['videoId'] + "/publish/")
print("Response: ", s.status_code, s.text)
s.raise_for_status()

print("Step 3: upload present video to Plvideo")

print("3.3: prepare to upload present")

print("fetching video signature")
sign = session.post("https://upload.plvideo.ru/ru/files/sign/", json=
                    {
                        "channelId": data['items'][0]['id'],
                        "fileName": os.path.basename(present),
                        "fileSize": os.path.getsize(present),
                        "fileType": mimetypes.guess_type(present)[0]
                    }).json()
print(sign)
print("Video ID: ", sign['videoId'])
print("Sign: ", sign['sign'])

print("Allocating video ID")
session.post(f"https://studio-api.g1.plvideo.ru/v1/videos/{sign['videoId']}/create/").raise_for_status()

print("3.4: upload video as single chunk (it may take a while)")

print("Getting path")
chunk_upl = session.post("https://upload.plvideo.ru/ru/files/", headers=
             {"X-Sign": sign['sign'],
              "Tus-Resumable": "1.0.0",
              "Upload-Offset": "0",
              "Upload-Concat": "partial",
              "Upload-Length": str(os.path.getsize(present))
              })

chunk_upl.raise_for_status()

print("Uploading to path", chunk_upl.headers['Location'])

with open(present, 'rb') as f:
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
              "Upload-Metadata": "filename " + base64.b64encode(os.path.basename(present).encode('utf-8')).decode('utf-8')
               + ",filetype " + base64.b64encode(mimetypes.guess_type(present)[0].encode('utf-8')).decode('utf-8')})
print("Response: ", s.status_code, s.text)
s.raise_for_status()

print("3.5: finalize video metadata")

s = session.patch("https://studio-api.g1.plvideo.ru/v1/videos/" + sign['videoId'] + "/",
             json={
                 "cover": "blob:https://studio.plvideo.ru/" + str(uuid.uuid4()),
                 "visible": "link",
                 "playlistIds": [PLVIDEO_PLAYLIST_ID],
                 "tags": [],
                 "title": "Лабораторная работа No" + str(lab_number) + " презентация",
                 "description": ""
             })
print("Response: ", s.status_code, s.text)
s.raise_for_status()

plvideo_present_url = f'https://plvideo.ru/watch?v={sign["videoId"]}'

print("3.6: wait for upload to be acknowledged")
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


print("3.7: publish video")
s = session.post("https://studio-api.g1.plvideo.ru/v1/videos/" + sign['videoId'] + "/publish/")
print("Response: ", s.status_code, s.text)
s.raise_for_status()


input("Press Enter to continue to Rutube...")


print("Step 4: Upload to Rutube")
print("4.1: go on Rutube and copy any request as curl")
req = convert_to_requests.curl_to_requests(input("Paste it here or empty to use request.txt: ") or open('request.txt').read())

session = requests.Session()
session.headers = req.headers
try: del session.headers['Accept-Encoding']
except: pass


print("4.2: check account")

account_data = session.get("https://studio.rutube.ru/api/accounts/visitor/?client=vulp").json()
print('Your email is: ', account_data['email'])
input("Press Enter to continue...")


print("4.3: preparing videos")
upload_data = session.post("https://studio.rutube.ru/api/uploader/upload_session/?client=vulp", json={"cancelToken": {"promise": {}}})
upload_data.raise_for_status()
upload_data = upload_data.json()
sid_work = upload_data['sid']
videoid_work = upload_data['video']
print(f"{sid_work=} {videoid_work=}")

upload_data = session.post("https://studio.rutube.ru/api/uploader/upload_session/?client=vulp", json={"cancelToken": {"promise": {}}})
upload_data.raise_for_status()
upload_data = upload_data.json()
sid_present = upload_data['sid']
videoid_present = upload_data['video']
print(f"{sid_present=} {videoid_present=}")

print("4.4: setting params")
patch_work = session.patch(f"https://studio.rutube.ru/api/video/{videoid_work}/?308&client=vl", data={"title": f"Лабораторная работа {lab_number} выполнение", "is_hidden": True, "category": "13", "is_adult": True})
patch_work.raise_for_status()
rutube_work_info = patch_work.json()

patch_present = session.patch(f"https://studio.rutube.ru/api/video/{videoid_present}/?308&client=vl", data={"title": f"Лабораторная работа {lab_number} презентация", "is_hidden": True, "category": "13", "is_adult": True})
patch_present.raise_for_status()
rutube_present_info = patch_present.json()

rutube_work_url = rutube_work_info['video_url']
rutube_present_url = rutube_present_info['video_url']

print("4.5 upload data (may take a while)")
print("Uploading work...")
req = session.post(f"https://u.rutube.ru/upload/{sid_work}", files={'data': open(work, 'rb')})
print(req, req.text)

print("Uploading present...")
req = session.post(f"https://u.rutube.ru/upload/{sid_present}", files={'data': open(present, 'rb')})
print(req, req.text)

print("4.6 add to playlist")
p = session.post(f"https://studio.rutube.ru/api/playlist/custom/{RUTUBE_PLAYLIST_ID}", json={"video_ids": [videoid_work]})
print(p, p.text)
p = session.post(f"https://studio.rutube.ru/api/playlist/custom/{RUTUBE_PLAYLIST_ID}", json={"video_ids": [videoid_present]})
print(p, p.text)
print("N. B. This is likely to fail due to a lack of CSRF token. If so, go on https://studio.rutube.ru/videos and set playlist manually")


input("Press Enter to continue to building documents...")

print("Step 5: build documents")

cwd = os.getcwd()
os.chdir(f"../labs/lab{lab_number}/report")
os.system("make")
os.chdir("../presentation")
makefile = open("Makefile").read()
makefile = makefile.replace("xelatex", "lualatex")
open("Makefile", "w").write(makefile)
os.system("make")

os.chdir("..")

print("Step 6: collecting files")

gh = os.path.join(cwd, "github")
mo = os.path.join(cwd, "moodle")
if os.path.exists(gh):
    print(f"Removing {gh}")
    shutil.rmtree(gh)
if os.path.exists(mo):
    print(f"Removing {mo}")
    shutil.rmtree(mo)
os.makedirs(gh)
os.makedirs(mo)

import shutil
shutil.copy("report/report.md", gh)  # отчёт в markdown (в каталоге git и в файлах релиза);
shutil.copy("report/report.docx", gh)  # отчёт в docx (сделанный из markdown) (приложено к ответу и в файлах релиза);
shutil.copy("report/report.docx", mo)
shutil.copy("report/report.pdf", gh)  # отчёт в pdf (сделанный из markdown) (приложено к ответу и в файлах релиза);
shutil.copy("report/report.pdf", mo)

os.system(f"zip -r /tmp/lab{lab_number}.zip *")
shutil.copy(f"/tmp/lab{lab_number}.zip", mo)  # архив с исходными материалами markdown (текстовые файлы, скриншоты и т. д.);
shutil.copy(f"/tmp/lab{lab_number}.zip", gh)

shutil.copy("presentation/presentation.pdf", gh)  # презентацию в pdf и html (сделанные из markdown) (приложено к ответу и в файлах релиза);
shutil.copy("presentation/presentation.html", gh)
shutil.copy("presentation/presentation.pdf", mo)
shutil.copy("presentation/presentation.html", mo)

shutil.copy("presentation/presentation.md", gh)  # презентацию в markdown (в каталоге git и в файлах релиза).

print("Step 7: Github Release")
print("Go to:")
print(f"\thttps://github.com/{GH_REPO}/releases/new")
print("then create a new release.")
print("Upload all files from:")
print("\t", gh)

release_tag = input("Please enter the release tag here (like v0.1.0): ")

print("Step 8: Moodle submission")
print("Go to:")
print("\t https://esystem.rudn.ru/course/view.php?id=11801#section-10")
print("and draft a new submission for lab", lab_number)

print("Upload all files from:")
print("\t", mo)

print("Use this as body text:")
print("---")

print("Лаб", lab_number)
print()
print("RUTUBE:")
print(f"Плейлист: https://rutube.ru/plst/{RUTUBE_PLAYLIST_ID}")
print(f"Выполнение: {rutube_work_url}")
print(f"Подготовка отчета: {rutube_work_url}")
print(f"Подготовка презентации: {rutube_work_url}")
print(f"Презентация: {rutube_present_url}")

print()
print("PLVIDEO:")
print(f"Плейлист: https://plvideo.ru/playlist?list={PLVIDEO_PLAYLIST_ID}")
print(f"Выполнение: {plvideo_work_url}")
print(f"Подготовка отчета: {plvideo_work_url}")
print(f"Подготовка презентации: {plvideo_work_url}")
print(f"Презентация: {plvideo_present_url}")

print("GITHUB:")
print(f"Репозиторий: https://github.com/{GH_REPO}")
print(f"Релиз: https://github.com/{GH_REPO}/releases/tag/{release_tag}")

print()
print("---")
print("When you're done, you can clean up with:")
print()
print("rm -r", gh)
print("rm -r", mo)
print("rm ./meta.json ./work.json ./present.json")
print("rm", work)
print("rm", present)