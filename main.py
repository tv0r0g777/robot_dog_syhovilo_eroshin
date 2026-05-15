import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import threading
import time


CAMERA_SOURCE = 0  # потом заменим на камеру собаки через кабель/IP


class GuardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Охрана лаборатории — робот-собака")
        self.root.geometry("850x650")

        self.cap = None
        self.is_camera_running = False
        self.is_guard_active = False

        self.prev_gray = None
        self.last_check_time = 0
        self.check_interval = 3  # проверка каждые 3 секунды
        self.motion_threshold = 1000000

        self.status_label = tk.Label(
            root,
            text="Статус: неактивно",
            font=("Arial", 16)
        )
        self.status_label.pack(pady=10)

        self.video_label = tk.Label(root, bg="black")
        self.video_label.pack(pady=10)

        self.alarm_label = tk.Label(
            root,
            text="",
            font=("Arial", 18, "bold"),
            fg="red"
        )
        self.alarm_label.pack(pady=10)

        buttons_frame = tk.Frame(root)
        buttons_frame.pack(pady=10)

        self.check_button = tk.Button(
            buttons_frame,
            text="Проверить подключение",
            font=("Arial", 13),
            command=self.check_connection
        )
        self.check_button.grid(row=0, column=0, padx=10)

        self.start_button = tk.Button(
            buttons_frame,
            text="Включить режим охраны",
            font=("Arial", 13),
            command=self.start_guard
        )
        self.start_button.grid(row=0, column=1, padx=10)

        self.stop_button = tk.Button(
            buttons_frame,
            text="Выключить режим охраны",
            font=("Arial", 13),
            command=self.stop_guard
        )
        self.stop_button.grid(row=0, column=2, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def check_connection(self):
        cap = cv2.VideoCapture(CAMERA_SOURCE)

        if cap.isOpened():
            messagebox.showinfo("Подключение", "Камера подключена успешно")
        else:
            messagebox.showerror("Ошибка", "Камера не найдена")

        cap.release()

    def start_camera(self):
        if self.is_camera_running:
            return

        self.cap = cv2.VideoCapture(CAMERA_SOURCE)

        if not self.cap.isOpened():
            messagebox.showerror("Ошибка", "Не удалось открыть камеру")
            return

        self.is_camera_running = True
        self.update_frame()

    def start_guard(self):
        self.start_camera()

        if not self.is_camera_running:
            return

        self.is_guard_active = True
        self.status_label.config(text="Статус: активно")
        self.alarm_label.config(text="")
        self.prev_gray = None

    def stop_guard(self):
        self.is_guard_active = False
        self.status_label.config(text="Статус: неактивно")
        self.alarm_label.config(text="")

    def update_frame(self):
        if not self.is_camera_running or self.cap is None:
            return

        ret, frame = self.cap.read()

        if ret:
            frame = cv2.resize(frame, (760, 430))

            if self.is_guard_active:
                self.detect_motion(frame)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=image)

            self.video_label.imgtk = photo
            self.video_label.config(image=photo)

        self.root.after(30, self.update_frame)

    def detect_motion(self, frame):
        current_time = time.time()

        if current_time - self.last_check_time < self.check_interval:
            return

        self.last_check_time = current_time

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.prev_gray is None:
            self.prev_gray = gray
            return

        diff = cv2.absdiff(self.prev_gray, gray)
        _, thresh =

cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        motion_score = thresh.sum()

        if motion_score > self.motion_threshold:
            self.alarm_label.config(text="ТРЕВОГА! КТО-ТО ВОШЁЛ В ПОМЕЩЕНИЕ")
        else:
            self.alarm_label.config(text="")

        self.prev_gray = gray

    def on_close(self):
        self.is_camera_running = False
        self.is_guard_active = False

        if self.cap:
            self.cap.release()

        self.root.destroy()


root = tk.Tk()
app = GuardApp(root)
root.mainloop()