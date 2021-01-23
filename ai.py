import wave
import json
import requests
from aip import AipSpeech
import cv2
from time import sleep
from picamera import PiCamera

def camera(filename="output.jpg"):
    camera = PiCamera()
    camera.resolution = (1024, 768)
    sleep(2)
    camera.capture(filename)
    camera.close()

# 以下换成自己的百度云语音API KEY
APP_ID = '9670645'
API_KEY = 'qg4haN8b2bGvFtCbBGqhrmZy'
SECRET_KEY = '585d4eccb50d306c401d7df138bb02e7'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

# 语音识别
def asr(f):
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

