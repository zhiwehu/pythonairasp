import wave
import json
import requests
from aip import AipSpeech
import cv2
from time import sleep
from picamera import PiCamera
from pytesseract import image_to_string


def oci(filename="output.jpg"):
    config = r'--tessdata-dir "./data/"'
    text = image_to_string(filename, 'chi_sim', config=config).strip()
    return text


# 导入人脸模型数据
face_cascade = cv2.CascadeClassifier("cv2models/haarcascade_frontalface_default.xml")


# 检测人脸的自定义函数
def __detect_face(frame):
    # 识别人脸并保存到一个列表中
    faces = face_cascade.detectMultiScale(frame, 1.3, 5)
    # 列表中的每个人脸数据都是由4个值组成的：
    # x,y表示左上角的位置，w,h表示宽度和高度，对每张人脸，我们画一个蓝色方框来框起来
    if len(faces) > 0:
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), ((x + w), (y + h)), (0, 0, 255), 2)
    return len(faces), frame


def face(quit_when_detect_face=False):
    # 打开摄像头
    cap = cv2.VideoCapture(0)

    while True:
        # 从摄像头读取数据
        ret, frame = cap.read()
        if ret:
            # 检测人脸
            faces, frame = __detect_face(frame)
            # 显示视频数据
            cv2.imshow("video", frame)
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


# 以下换成自己的百度云语音API KEY
APP_ID = '23549160'
API_KEY = 'MeyxezlB82jwihFtXT7Kdt7i'
SECRET_KEY = 'BVeGYZ5DyP88IvquiNKm6kkW07m2Dhi8'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


# 语音识别
def asr(f="output.wav"):
    wav = wave.open(f, 'rb')
    res = client.asr(wav.readframes(wav.getnframes()), 'pcm', 16000, {
        'dev_pid': 1936,
    })
    if res['err_no'] == 0:
        return ''.join(res['result'])
    else:
        return ''


# 语音合成
def tts(s):
    # per参数为发音人选择, 0为女声，1为男声，
    # 3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
    result = client.synthesis(s, 'zh', 3, {'per': 4})
    # 识别正确返回语音二进制
    if not isinstance(result, dict):
        with open("temp.mp3", "wb") as f:
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
                "apiKey": "98f95153fb5c4684a5602b909949ba61",
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

    # 设置30帧/秒，分辨率是1280x720，保存在当前目录下的output.avi文件
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
