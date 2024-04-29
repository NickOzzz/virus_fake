import cv2
import json
import time
import ctypes
from random import randrange

priority_queue = {}


class JsonReader:
    def __init__(self, path):
        with open(path) as p:
            self.content = json.load(p)

    def read(self, key):
        return self.content[key]


class VideoProperties:
    def __init__(self, path, name, x_pos, y_pos, x_size, y_size, priority):
        self.path = path
        self.name = name,
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_size = x_size
        self.y_size = y_size
        self.priority = priority
        self.videoCapture = cv2.VideoCapture(self.path)


def read_and_show_looped_video(config, list_video_properties):
    window_closed = False

    for name in [prop.name[0] for prop in list_video_properties]:
        priority_queue[name] = window_closed

    while True:
        for prop in list_video_properties:
            name = prop.name[0]
            read_success, frame = prop.videoCapture.read()
            if read_success:
                if priority_queue[name]:
                    continue
                full_screen = config.read("full_screen")
                cv2.namedWindow(name, cv2.WND_PROP_FULLSCREEN)
                (cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN,
                                       cv2.WINDOW_FULLSCREEN if full_screen else cv2.WINDOW_NORMAL))
                cv2.resizeWindow(name, prop.x_size, prop.y_size)
                if prop.priority:
                    cv2.setWindowProperty(name, cv2.WND_PROP_TOPMOST, 1)
                cv2.moveWindow(name, prop.x_pos, prop.y_pos)
                cv2.imshow(name, frame)
                cv2.setMouseCallback(name, close_window, name)
            else:
                continue

        if cv2.waitKey(1) == 27:
            for i in priority_queue:
                priority_queue[i] = True
            break

        if False not in priority_queue.values():
            break

    cv2.destroyAllWindows()


def close_window(event, x, y, flags, name):
    if event == cv2.EVENT_LBUTTONDOWN:
        priority_queue[name] = True
        cv2.destroyWindow(name)


def get_main_video():
    config = JsonReader("build/appsettings.json")
    path = config.read("main_path")
    return VideoProperties(path, path, 0, 0, 1920, 1080, priority=False)


def get_secondary_video():
    config = JsonReader("build/appsettings.json")
    x_pos = randrange(1620)
    y_pos = randrange(500)
    path = config.read("secondary_path")
    return VideoProperties(path, path + str(x_pos + y_pos), x_pos, y_pos, 350, 550, priority=True)


try:
    if __name__ == '__main__':
        init_config = JsonReader("build/appsettings.json")
        video_properties = []
        video_properties.append(get_main_video())

        for index in range(init_config.read("amount_of_messages")):
            video_properties.append(get_secondary_video())

        read_and_show_looped_video(init_config, video_properties)

except Exception as ex:
    ctypes.windll.user32.MessageBoxW(0, ex, "Error", 1)

