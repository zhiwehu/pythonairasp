# -*- coding: UTF-8 -*-

import json
import requests
from aip import AipSpeech, AipFace
import cv2
from picamera import PiCamera
from pytesseract import image_to_string
import base64
import uuid
from voiceutils import *

# 百度云语音API KEY，请注册百度AI云服务，换成自己的，否则可能不能正常使用哦
VOICE_APP_ID = '23549160'
VOICE_API_KEY = 'MeyxezlB82jwihFtXT7Kdt7i'
VOICE_SECRET_KEY = 'BVeGYZ5DyP88IvquiNKm6kkW07m2Dhi8'
voice_client = AipSpeech(VOICE_APP_ID, VOICE_API_KEY, VOICE_SECRET_KEY)

# 图灵机器人API KEY，请注册自己的图灵机器人，否则可能不能正常使用哦。
TULING_API_KEY = "98f95153fb5c4684a5602b909949ba61"

# 百度云人脸识别API KEY，请注册百度AI云服务，换成自己的，否则可能不能正常使用哦
FACE_APP_ID = '23581750'
FACE_API_KEY = 'ww7tyu9ix03GF89B6HcLXLVj'
FACE_SECRET_KEY = 'CA4LOIEMWpLB6WzLUdEhi1TSo5KQ1DUS'
face_client = AipFace(FACE_APP_ID, FACE_API_KEY, FACE_SECRET_KEY)

# 导入人脸模型数据
face_cascade = cv2.CascadeClassifier("cv2models/haarcascade_frontalface_default.xml")


def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def oci(filename="output.jpg"):
    config = r'--tessdata-dir "./data/"'
    text = image_to_string(filename, 'chi_sim', config=config).strip()
    return text


# 检测人脸的自定义函数
def __detect_face(frame):
    # 识别人脸并保存到一个列表中
    faces = face_cascade.detectMultiScale(frame, 1.3, 5)
    # 列表中的每个人脸数据都是由4个值组成的：
    # x,y表示左上角的位置，w,h表示宽度和高度，对每张人脸，我们画一个蓝色方框来框起来
    if len(faces) > 0:
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), ((x + w), (y + h)), (0, 0, 255), 2)
            print(x, y, w, h)
    return len(faces), frame


def face(quit_when_detect_face=False):
    # 打开摄像头
    cap = cv2.VideoCapture(0)

    while True:
        # 从摄像头读取数据
        ret, frame = cap.read()
        if ret:
            # 检测人脸
            faces, newframe = __detect_face(frame)
            # 显示视频数据
            cv2.imshow("video", newframe)
            # 让这一帧停留1毫秒，这时如果我们按下q键，就跳出这个循环停止播放
            # 如果不写cv2.waitKey()我们将看不到视频图像
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

            if faces > 0 and quit_when_detect_face:
                cv2.imwrite("face.jpg", frame)
                break

    # 关闭摄像头
    cap.release()
    # 关闭播放器
    cv2.destroyAllWindows()


# 拍照
def camera(filename="output.jpg"):
    camera = PiCamera()
    camera.resolution = (1024, 768)
    camera.capture(filename)
    camera.close()
    return filename


# 人脸识别
def people(filename="face.jpg"):
    image_str = get_base64_encoded_image(filename)

    imageType = "BASE64"
    groupIdList = "1"

    """ 如果有可选参数 """
    options = {}
    # options["max_face_num"] = 3
    options["match_threshold"] = 70
    # options["quality_control"] = "NORMAL"
    # options["liveness_control"] = "LOW"
    # options["user_id"] = "233451"

    """ 带参数调用人脸搜索 """
    resp = face_client.search(image_str, imageType, groupIdList, options)
    print(resp)
    if resp['error_code'] == 222207:
        # add_people(image_str)
        return None
    if resp['error_code'] == 0:
        name = resp['result']['user_list'][0]['user_info']
        # say("{}，我们又见面啦！最近你都干什么去了呢？".format(name))
        return name


# 往百度云人脸识别库中增加一张人脸照片
def add_people(name, filename="face.jpg"):
    image_str = get_base64_encoded_image(filename)
    name = name.encode('utf-8').decode('latin1')
    imageType = "BASE64"
    groupId = "1"
    userId = str(uuid.uuid4())[:8]
    options = {}
    options["user_info"] = name

    """ 调用人脸注册 """
    resp = face_client.addUser(image_str, imageType, groupId, userId, options)
    print(resp)
    if resp['error_code'] == 0:
        return True
    else:
        return False


# 语音识别
def asr(f="output.wav"):
    wav = wave.open(f, 'rb')
    res = voice_client.asr(wav.readframes(wav.getnframes()), 'pcm', 16000, {
        'dev_pid': 1936,
    })
    if res['err_no'] == 0:
        return ''.join(res['result'])
    else:
        return ''


# 语音合成
def tts(s, filename="temp.mp3"):
    # per参数为发音人选择, 0为女声，1为男声，
    # 3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
    result = voice_client.synthesis(s, 'zh', 3, {'per': 4})
    # 识别正确返回语音二进制
    if not isinstance(result, dict):
        with open(filename, "wb") as f:
            f.write(result)
            tmpfile = f.name
            return tmpfile
    else:
        return None


# 智能对话
def chat(msg):
    try:
        url = "http://openapi.tuling123.com/openapi/api/v2"
        body = {
            "reqType": 0,
            "perception": {
                "inputText": {
                    "text": msg
                }
            },
            "userInfo": {
                "apiKey": TULING_API_KEY,
                "userId": "zhixinfuture"
            }
        }
        r = requests.post(url, data=json.dumps(body))
        resp = r.json()
        answer = resp["results"][0]["values"]["text"]
        return answer
    except Exception:
        return "抱歉, 我的大脑短路了，请稍后再试试."


def video(filename="output.avi"):
    # 打开摄像头
    cap = cv2.VideoCapture(0)

    # 设置30帧/秒，分辨率是640x480，保存在当前目录下的output.avi文件
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, 30.0, (640, 480))

    while True:
        # 从摄像头读取数据
        ret, frame = cap.read()
        if ret:
            # 显示视频数据
            cv2.imshow("video", frame)
            # 保存视频
            out.write(frame)
            # 让这一帧停留1毫秒，这时如果我们按下q键，就跳出这个循环停止播放
            # 如果不写cv2.waitKey()我们将看不到视频图像
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            if key == ord('c'):
                # 将当前这一帧保存为一个图片文件,保存在当前目录下test.jpg
                cv2.imwrite("picture.jpg", frame)

    # 关闭视频保存器
    out.release()
    # 关闭摄像头
    cap.release()
    # 关闭播放器
    cv2.destroyAllWindows()


def say(word):
    mp3 = tts(word)
    playsound(mp3)


def get_voice_text():
    record()
    text = asr()
    return text
