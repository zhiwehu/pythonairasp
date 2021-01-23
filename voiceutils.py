import pyaudio
import wave
import subprocess

def record(seconds=5, filename="output.wav"):
    chunk = 1024    # 单位数据
    sample_format = pyaudio.paInt16  # 16位采样精度
    channels = 2    # 双声道
    fs = 16000      # 采样率
    p = pyaudio.PyAudio()  # 创建一个录音机

    print('开始录音')

    # 打开录音机
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # 录音数据存储列表

    # 从录音机获取5秒的声音数据，并保存到存储列表中
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # 关闭录音机
    stream.stop_stream()
    stream.close()
    p.terminate()

    print('结束录音')

    # 将录音数据保存为一个声音文件
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

def play(filename="output.wav"):
    # 音频数据单位
    chunk = 1024  

    # 打开音频文件
    wf = wave.open(filename, 'rb')

    # 创建一个播放机
    p = pyaudio.PyAudio()

    # 打开音频文件，获取音频流
    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    # 读出数据
    data = wf.readframes(chunk)

    # 播放声音
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # 关闭播放机
    stream.close()
    p.terminate()
    wf.close()


def playsound(voice="output.wav"):
    cmd = ['play', voice]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.wait()

