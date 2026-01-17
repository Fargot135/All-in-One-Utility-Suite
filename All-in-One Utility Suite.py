import os
import tkinter as tk
from random import choice
from tkinter import messagebox
import requests
import urllib.parse
import math
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime
import customtkinter as ctk


class Config:
    """Конфігурація програми"""
    WINDOW_WIDTH = 1080
    WINDOW_HEIGHT = 720
    BG_COLOR = "#212121"
    PRIMARY_COLOR = "#ffa800"
    SECONDARY_COLOR = "#7c827d"
    
    # Wave animation
    WAVE_SPEED = 1.2
    WAVE_HEIGHT = 50
    WAVE_FREQUENCY = 80
    WAVE_BASE_Y = 800
    
    # API
    WEATHER_API_KEY = "YOUR_API_KEY_HERE"
    WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/forecast"
    
    # Files
    IDEAS_FILE = 'How.txt'
    IMAGES_DIR = "images"
    
    # Image offsets
    IMAGE_OFFSETS = {
        "weather": 65,
        "idea": 65,
        "training": 70
    }


class TextAnimator:
    """Клас для анімації тексту"""
    @staticmethod
    def animate(label, text, delay=50, index=0, callback=None):
        if index < len(text):
            label.config(text=text[:index + 1])
            label.after(delay, TextAnimator.animate, label, text, delay, index + 1, callback)
        elif callback:
            callback()


class WaveAnimation:
    """Анімація хвилі на фоні"""
    def __init__(self, canvas, config):
        self.canvas = canvas
        self.config = config
        self.offset = 0
        
    @staticmethod
    def rgb_to_hex(r, g, b):
        return f'#{int(r):02x}{int(g):02x}{int(b):02x}'
        
    def draw(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.canvas.delete("wave")
        
        r = 127 + 127 * math.sin(self.offset / 110)
        g = 127 + 127 * math.sin(self.offset / 120 + 2)
        b = 127 + 127 * math.sin(self.offset / 130 + 4)
        
        color1 = self.rgb_to_hex(r, g, b)
        dim_factor = 0.4
        color2 = self.rgb_to_hex(r * dim_factor, g * dim_factor, b * dim_factor)
        
        wave1 = {
            "color": color1,
            "height": self.config.WAVE_HEIGHT * 0.8,
            "frequency": self.config.WAVE_FREQUENCY * 1.5,
            "offset": self.offset,
        }
        wave2 = {
            "color": color2,
            "height": self.config.WAVE_HEIGHT * 0.5,
            "frequency": self.config.WAVE_FREQUENCY * 2.5,
            "offset": self.offset * 0.5,
        }
        
        self._draw_wave(wave2, canvas_height)
        self._draw_wave(wave1, canvas_height)
        
        self.offset += self.config.WAVE_SPEED
        self.canvas.after(16, self.draw)
        
    def _draw_wave(self, wave_data, canvas_height):
        points = []
        for x in range(0, 1660, 10):
            dyn_height = wave_data["height"] - 20 * math.sin(wave_data["offset"] / 30)
            y = self.config.WAVE_BASE_Y + dyn_height * math.sin(
                (x + wave_data["offset"]) / wave_data["frequency"]
            )
            points.append(x)
            points.append(y)
            
        for i in range(0, len(points) - 2, 2):
            x1, y1 = points[i], points[i + 1]
            x2, y2 = points[i + 2], points[i + 3]
            self.canvas.create_polygon(
                x1, y1, x2, y2, x2, canvas_height, x1, canvas_height,
                fill=wave_data["color"], outline="", tags="wave"
            )


class ImageManager:
    """Менеджер зображень"""
    def __init__(self, base_dir, window):
        self.base_dir = base_dir
        self.window = window
        self.images = {}
        self.animation_cancelled = False
        self.animation_in_progress = False
        self.is_image_shown = False
        self.image_label = tk.Label(window, borderwidth=0, bg=Config.BG_COLOR, highlightthickness=0)
        self.load_images()
        
    def get_path(self, filename):
        return os.path.join(self.base_dir, Config.IMAGES_DIR, filename)
        
    def load_images(self):
        image_configs = {
            "weather": "weather.png",
            "idea": "cube.png",
            "training": "dumbbell.png"
        }
        
        for key, filename in image_configs.items():
            img = Image.open(self.get_path(filename)).convert("RGBA")
            img_resized = img.resize((100, 100), Image.Resampling.LANCZOS)
            self.images[key] = ImageTk.PhotoImage(img_resized)
            
    def is_mouse_over_button(self, btn, event):
        btn_x1 = btn.winfo_rootx()
        btn_y1 = btn.winfo_rooty()
        btn_x2 = btn_x1 + btn.winfo_width()
        btn_y2 = btn_y1 + btn.winfo_height()
        return btn_x1 <= event.x_root <= btn_x2 and btn_y1 <= event.y_root <= btn_y2
        
    def show_image(self, event, image_key, btn):
        if self.is_image_shown or not self.is_mouse_over_button(btn, event):
            return
            
        self.animation_cancelled = False
        self.animation_in_progress = True
        self.image_label.config(image=self.images[image_key])
        self.image_label.image = self.images[image_key]
        
        def place_image():
            # Перевіряємо, чи кнопка все ще видима
            if not btn.winfo_ismapped():
                self.animation_in_progress = False
                return
                
            btn_x = btn.winfo_rootx() - self.window.winfo_rootx()
            btn_y = btn.winfo_rooty() - self.window.winfo_rooty()
            x_offset = Config.IMAGE_OFFSETS[image_key]
            final_x = btn_x + x_offset
            start_y = btn_y
            end_y = 90
            self.image_label.place(x=final_x, y=start_y)
            self.animate_show(start_y, end_y, final_x)
            
        self.window.after(1, place_image)
        self.is_image_shown = True
        
    def hide_image(self, event, btn):
        if self.animation_in_progress or self.is_mouse_over_button(btn, event):
            return
            
        self.animation_cancelled = False
        self.animation_in_progress = True
        start_y = self.image_label.winfo_y()
        final_x = self.image_label.winfo_x()
        end_y = btn.winfo_y()
        self.animate_hide(start_y, end_y, final_x, step=10)  # Збільшено крок з 5 до 10
        self.is_image_shown = False
        
    def animate_show(self, y_start, y_end, fixed_x, step=5):
        def move():
            nonlocal y_start
            if self.animation_cancelled:
                self.animation_in_progress = False
                return
            if y_start > y_end:
                y_start -= step
                self.image_label.place(x=fixed_x, y=y_start)
                self.window.after(5, move)
            else:
                self.image_label.place(x=fixed_x, y=y_end)
                self.animation_in_progress = False
        move()
        
    def animate_hide(self, y_start, y_end, fixed_x, step=10):
        def move():
            nonlocal y_start
            if self.animation_cancelled:
                self.animation_in_progress = False
                self.image_label.place_forget()
                return
            if y_start < y_end:
                y_start += step
                self.image_label.place(x=fixed_x, y=y_start)
                self.window.after(3, move)  # Зменшено затримку з 5 до 3 мс
            else:
                self.image_label.place_forget()
                self.window.update_idletasks()
                self.animation_in_progress = False
        move()


class WeatherService:
    """Сервіс для роботи з погодою"""
    def __init__(self, api_key):
        self.api_key = api_key
        
    def fetch_weather(self, city):
        city_encoded = urllib.parse.quote(city)
        url = f"{Config.WEATHER_API_URL}?q={city_encoded}&appid={self.api_key}&units=metric&lang=en"
        response = requests.get(url)
        data = response.json()
        
        if data["cod"] == "200":
            return data
        return None


class IdeasManager:
    """Менеджер для роботи з ідеями"""
    def __init__(self, filepath):
        self.filepath = filepath
        
    def add_idea(self, idea):
        if not idea.strip():
            raise ValueError("The input field is blank")
            
        with open(self.filepath, 'a+', encoding="utf-8") as file:
            file.write(idea + '\n')
            
    def get_random_idea(self):
        try:
            with open(self.filepath, 'r', encoding="utf-8") as file:
                lines = file.readlines()
                return choice(lines).strip() if lines else "File empty"
        except FileNotFoundError:
            return "File not found"


class Application:
    """Головний клас програми"""
    def __init__(self):
        self.window = ctk.CTk()
        self.config = Config()
        self.animation_running = False
        self.setup_window()
        self.setup_canvas()
        self.image_manager = ImageManager(os.path.dirname(__file__), self.window)
        self.weather_service = WeatherService(Config.WEATHER_API_KEY)
        self.ideas_manager = IdeasManager(Config.IDEAS_FILE)
        self.setup_ui()
        
    def setup_window(self):
        self.window.resizable(False, False)
        self.window.title("PET-project")
        self.window.geometry(f'{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}')
        self.window.configure(fg_color=Config.BG_COLOR)
        
    def setup_canvas(self):
        self.canvas = tk.Canvas(
            self.window,
            width=Config.WINDOW_WIDTH,
            height=Config.WINDOW_HEIGHT,
            bg=Config.BG_COLOR,
            bd=0,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.wave_animation = WaveAnimation(self.canvas, self.config)
        self.wave_animation.draw()
        
    def setup_ui(self):
        self.create_back_button()
        self.create_main_screen()
        
    def create_back_button(self):
        self.back_button = tk.Button(
            self.window,
            text="←BACK",
            font=("ARIAL BLACK", 15),
            command=self.back_to_main,
            bg='#ff3600',
            fg='white'
        )
        
    def create_main_screen(self):
        self.main_label = tk.Label(
            self.window,
            text="CHOOSE A FUNCTION:",
            font=("WIDE LATIN", 25),
            fg=Config.PRIMARY_COLOR,
            bg=Config.BG_COLOR
        )
        self.main_label.place(x=460, y=50)
        
        button_configs = [
            ("weather", 157.5, self.open_weather, "#57f7f2"),
            ("randomiser", 465, self.open_ideas, "#6d1ae6"),
            ("training", 772.5, self.open_training, "#1dd75a")
        ]
        
        self.main_buttons = {}
        for text, x, command, hover_color in button_configs:
            btn = ctk.CTkButton(
                self.window,
                text=self.vertical_text(text),
                font=ctk.CTkFont("Consolas", 25),
                fg_color=Config.SECONDARY_COLOR,
                text_color=Config.BG_COLOR,
                hover_color=hover_color,
                corner_radius=15,
                command=command,
                width=150,
                height=360
            )
            btn.place(x=x, y=127)
            self.main_buttons[text] = btn
            
            # Прив'язка подій для анімації зображень
            image_key = "idea" if text == "randomiser" else text
            btn.bind("<Enter>", lambda e, key=image_key, b=btn: self.image_manager.show_image(e, key, b))
            btn.bind("<Leave>", lambda e, b=btn: self.image_manager.hide_image(e, b))
            
    @staticmethod
    def vertical_text(text):
        return "\n".join(text)
        
    def clear_window(self):
        # Скасовуємо всі анімації перед очищенням
        self.image_manager.animation_cancelled = True
        self.image_manager.is_image_shown = False
        self.image_manager.image_label.place_forget()
        
        for widget in self.window.winfo_children():
            widget.place_forget()
            
    def stop_animation(self):
        self.animation_running = False
        
    def back_to_main(self):
        self.stop_animation()
        # Скидаємо стан анімації зображень
        self.image_manager.animation_cancelled = True
        self.image_manager.animation_in_progress = False
        self.image_manager.is_image_shown = False
        self.image_manager.image_label.place_forget()
        
        self.clear_window()
        self.main_label.place(x=460, y=50)
        for text, btn in self.main_buttons.items():
            if text == "weather":
                btn.place(x=157.5, y=127)
            elif text == "randomiser":
                btn.place(x=465, y=127)
            elif text == "training":
                btn.place(x=772.5, y=127)
            
    def open_weather(self):
        self.clear_window()
        self.back_button.place(x=0, y=0)
        
        weather_label = tk.Label(
            self.window,
            text="Enter city name:",
            font=("WIDE LATIN", 30),
            bg=Config.BG_COLOR,
            fg=Config.PRIMARY_COLOR
        )
        weather_label.place(x=525, y=80)
        
        city_entry = tk.Text(
            self.window,
            font=("Arial", 20),
            width=50,
            height=2,
            fg=Config.PRIMARY_COLOR,
            bg="#02325e",
            bd=0,
            highlightthickness=8,
            highlightbackground=Config.PRIMARY_COLOR,
            highlightcolor=Config.PRIMARY_COLOR
        )
        city_entry.place(x=410, y=200)
        
        def fetch():
            city = city_entry.get("1.0", "end-1c").strip()
            if city:
                try:
                    data = self.weather_service.fetch_weather(city)
                    if data:
                        self.show_weather_window(city, data)
                    else:
                        messagebox.showinfo("Error", "City not found.")
                except Exception as e:
                    messagebox.showinfo("Error", f"Failed to retrieve weather: {e}")
            else:
                messagebox.showinfo("Error", "The input field is empty.")
                
        submit_button = ctk.CTkButton(
            self.window,
            text="Get Weather",
            font=ctk.CTkFont("Consolas", 25),
            fg_color=Config.SECONDARY_COLOR,
            text_color=Config.BG_COLOR,
            hover_color="#02325e",
            corner_radius=15,
            command=fetch,
            width=300,
            height=70
        )
        submit_button.place(x=375, y=250)
        city_entry.bind('<Return>', lambda e: fetch())
        
    def show_weather_window(self, city, data):
        current_data = data["list"][0]
        current_temp = current_data["main"]["temp"]
        current_condition = current_data["weather"][0]["description"]
        current_humidity = current_data["main"]["humidity"]
        current_wind = current_data["wind"]["speed"]
        icon_code = current_data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        
        icon_response = requests.get(icon_url)
        icon_image = Image.open(BytesIO(icon_response.content)).resize((160, 160))
        icon_photo = ImageTk.PhotoImage(icon_image)
        
        weather_window = tk.Toplevel()
        weather_window.title(f"Weather forecast for {city}")
        weather_window.geometry("720x1080")
        weather_window.configure(bg='#e0f7fa')
        
        city_label = tk.Label(
            weather_window,
            text=f"Weather in {city}",
            font=("Arial", 28, "bold"),
            bg='#e0f7fa'
        )
        city_label.pack(pady=30)
        
        icon_label = tk.Label(weather_window, image=icon_photo, bg='#e0f7fa')
        icon_label.image = icon_photo
        icon_label.pack()
        
        current_info_text = (
            f"🌡 Temperature: {current_temp}°C\n"
            f"🌥 Conditions: {current_condition}\n"
            f"💧 Humidity: {current_humidity}%\n"
            f"💨 Wind: {current_wind} m/s"
        )
        current_info_label = tk.Label(
            weather_window,
            text=current_info_text,
            font=("Arial", 16),
            bg='#e0f7fa',
            justify='left'
        )
        current_info_label.pack(pady=30)
        
        forecast_label = tk.Label(
            weather_window,
            text="3-day Forecast:",
            font=("Arial", 20, "bold"),
            bg='#e0f7fa'
        )
        forecast_label.pack(pady=30)
        
        for i in range(1, 4):
            forecast_data = data["list"][i * 8]
            forecast_temp = forecast_data["main"]["temp"]
            forecast_condition = forecast_data["weather"][0]["description"]
            forecast_icon_code = forecast_data["weather"][0]["icon"]
            forecast_icon_url = f"http://openweathermap.org/img/wn/{forecast_icon_code}@2x.png"
            
            forecast_icon_response = requests.get(forecast_icon_url)
            forecast_icon_image = Image.open(BytesIO(forecast_icon_response.content)).resize((100, 100))
            forecast_icon_photo = ImageTk.PhotoImage(forecast_icon_image)
            
            forecast_dt = datetime.fromtimestamp(forecast_data["dt"])
            day_name = forecast_dt.strftime("%A").capitalize()
            
            forecast_info_text = (
                f"{day_name}:\n"
                f"🌡 Temperature: {forecast_temp}°C\n"
                f"🌥 Conditions: {forecast_condition}\n"
            )
            
            forecast_frame = tk.Frame(weather_window, bg='#e0f7fa')
            forecast_frame.pack(pady=10)
            
            forecast_icon_label = tk.Label(forecast_frame, image=forecast_icon_photo, bg='#e0f7fa')
            forecast_icon_label.image = forecast_icon_photo
            forecast_icon_label.pack(side="left")
            
            forecast_text_label = tk.Label(
                forecast_frame,
                text=forecast_info_text,
                font=("Arial", 14),
                bg='#e0f7fa',
                justify='left'
            )
            forecast_text_label.pack(side="left", padx=15)
            
        close_button = tk.Button(
            weather_window,
            text="Close",
            command=weather_window.destroy,
            font=("Arial", 16)
        )
        close_button.pack(pady=30)
        
    def open_ideas(self):
        self.clear_window()
        self.back_button.config(command=self.back_to_main)
        self.back_button.place(x=0, y=0)
        
        idea_label = tk.Label(
            self.window,
            text="Enter the option",
            font=("WIDE LATIN", 30),
            fg=Config.PRIMARY_COLOR,
            bg=Config.BG_COLOR
        )
        idea_label.place(x=525, y=80)
        
        enter_text = tk.Text(
            self.window,
            font=("Arial", 20),
            width=50,
            height=2,
            fg=Config.PRIMARY_COLOR,
            bg="#19015c",
            bd=0,
            highlightthickness=8,
            highlightbackground=Config.PRIMARY_COLOR,
            highlightcolor=Config.PRIMARY_COLOR
        )
        enter_text.place(x=410, y=200)
        
        def add_idea():
            value = enter_text.get("1.0", "end-1c")
            try:
                self.ideas_manager.add_idea(value)
                enter_text.delete("1.0", "end")
            except ValueError as e:
                messagebox.showinfo("Error", str(e))
                
        def random_idea():
            idea = self.ideas_manager.get_random_idea()
            messagebox.showinfo("Randomiser", idea)
            
        btn_add = ctk.CTkButton(
            self.window,
            text="Add a variant",
            font=ctk.CTkFont("Consolas", 25),
            fg_color=Config.SECONDARY_COLOR,
            text_color=Config.BG_COLOR,
            hover_color="#19015c",
            corner_radius=15,
            command=add_idea,
            width=100,
            height=50
        )
        btn_add.place(x=273, y=210)
        
        btn_show = ctk.CTkButton(
            self.window,
            text="Random selection",
            font=ctk.CTkFont("Consolas", 25),
            fg_color=Config.SECONDARY_COLOR,
            text_color=Config.BG_COLOR,
            hover_color="#1dd75a",
            corner_radius=15,
            command=random_idea,
            width=100,
            height=50
        )
        btn_show.place(x=530, y=210)
        
        enter_text.bind('<Return>', lambda e: add_idea())
        
    def open_training(self):
        self.clear_window()
        self.stop_animation()
        
        training_label = tk.Label(
            self.window,
            text="Select a training program",
            font=("WIDE LATIN", 30),
            fg=Config.PRIMARY_COLOR,
            bg=Config.BG_COLOR
        )
        training_label.place(x=390, y=80)
        
        programs = [
            ("split", 157.5, "#c41b1b", self.show_split_program),
            ("Full body", 465, "#026e06", self.show_full_body_program),
            ("Upper/Lower", 772.5, "#0642cc", self.show_upper_lower_program)
        ]
        
        for text, x, hover_color, command in programs:
            btn = ctk.CTkButton(
                self.window,
                text=self.vertical_text(text),
                command=command,
                width=150,
                height=360,
                corner_radius=15,
                text_color=Config.BG_COLOR,
                font=ctk.CTkFont("Consolas", 25),
                fg_color=Config.SECONDARY_COLOR,
                hover_color=hover_color
            )
            btn.place(x=x, y=127)
            
        self.back_button.config(command=self.back_to_main)
        self.back_button.place(x=0, y=0)
        
    def show_split_program(self):
        self.clear_window()
        self.stop_animation()
        
        label = tk.Label(
            self.window,
            text="Split Training Program",
            font=("WIDE LATIN", 35),
            fg="#c41b1b",
            bg=Config.BG_COLOR
        )
        label.place(x=335, y=80)
        
        self.back_button.config(command=self.open_training)
        self.back_button.place_forget()
        self.animation_running = True
        
        # Days
        days_data = [
            ("Day 1", 100, [
                "1. Bench Press",
                "2. Incline Dumbbell Press",
                "3. Dips",
                "4. Dumbbell Flyes",
                "5. Tricep Pushdowns"
            ]),
            ("Day 2", 650, [
                "1. Pull-ups",
                "2. Barbell Rows",
                "3. Lat Pulldown",
                "4. Dumbbell Rows",
                "5. Barbell Curls"
            ]),
            ("Day 3", 1100, [
                "1. Barbell Squats",
                "2. Leg Press",
                "3. Romanian Deadlifts",
                "4. Seated Shoulder Press",
                "5. Lateral Raises"
            ])
        ]
        
        for day_name, x_pos, exercises in days_data:
            day_label = tk.Label(self.window, text="", font=("ARIAL BLACK", 25), fg="#04b39e", bg=Config.BG_COLOR)
            day_label.place(x=x_pos, y=290)
            TextAnimator.animate(day_label, day_name)
            
            for i, exercise in enumerate(exercises):
                ex_label = tk.Label(self.window, text="", font=("Consolas", 20), fg="#6d45ff", bg=Config.BG_COLOR)
                ex_label.place(x=x_pos, y=350 + i * 40)
                TextAnimator.animate(ex_label, exercise)
                
        # Sets/Reps
        sets_reps = [
            (320, 345, "4x8"), (485, 385, "4x10"), (215, 425, "3x10"), (365, 465, "3x12"), (395, 505, "3x12"),
            (825, 345, "4x8"), (890, 385, "4x10"), (890, 425, "3x10"), (900, 465, "3x12"), (900, 505, "3x12"),
            (1370, 345, "4x8"), (1297, 385, "4x10"), (1430, 425, "3x10"), (1475, 465, "4x8"), (1370, 505, "3x15")
        ]
        
        self.window.after(1000, lambda: self.show_sets_reps(sets_reps))
        
    def show_full_body_program(self):
        self.clear_window()
        self.stop_animation()
        
        label = tk.Label(
            self.window,
            text="Full Body Program",
            font=("WIDE LATIN", 35),
            fg="#026e06",
            bg=Config.BG_COLOR
        )
        label.place(x=385, y=80)
        
        self.back_button.config(command=self.open_training)
        self.back_button.place_forget()
        self.animation_running = True
        
        days_data = [
            ("Day 1", 100, [
                "1. Barbell Squats",
                "2. Bench Press",
                "3. Bent-over Rows",
                "4. Bicep Curls",
                "5. Crunches (Abs)"
            ]),
            ("Day 2", 650, [
                "1. Romanian Deadlifts",
                "2. Shoulder Press",
                "3. Lat Pulldown",
                "4. Forward Lunges",
                "5. Plank (40 seconds)"
            ]),
            ("Day 3", 1100, [
                "1. Leg Press",
                "2. Dumbbell Bench Press",
                "3. One-Arm Dumbbell Row",
                "4. Bicep Curls + Triceps Ext",
                "5. Crunches (Abs)"
            ])
        ]
        
        for day_name, x_pos, exercises in days_data:
            day_label = tk.Label(self.window, text="", font=("ARIAL BLACK", 25), fg="#04b39e", bg=Config.BG_COLOR)
            day_label.place(x=x_pos, y=290)
            TextAnimator.animate(day_label, day_name)
            
            for i, exercise in enumerate(exercises):
                ex_label = tk.Label(self.window, text="", font=("Consolas", 20), fg="#6d45ff", bg=Config.BG_COLOR)
                ex_label.place(x=x_pos, y=350 + i * 40)
                TextAnimator.animate(ex_label, exercise)
                
        sets_reps = [
            (365, 345, "5×5"), (320, 385, "5×5"), (365, 425, "4×8"), (320, 465, "3x10"), (365, 505, "3x15"),
            (975, 345, "4x10"), (915, 385, "3x12"), (885, 425, "3x10"), (920, 465, "3x10per leg"), (970, 505, "3x40sec"),
            (1290, 345, "4x12"), (1370, 385, "4x10"), (1455, 425, "4x10"), (1535, 465, "3x12"), (1362, 505, "3x20")
        ]
        
        self.window.after(1000, lambda: self.show_sets_reps(sets_reps))
        
    def show_upper_lower_program(self):
        self.clear_window()
        self.stop_animation()
        
        label = tk.Label(
            self.window,
            text="Upper/Lower Program",
            font=("WIDE LATIN", 35),
            fg="#0642cc",
            bg=Config.BG_COLOR
        )
        label.place(x=335, y=80)
        
        self.back_button.config(command=self.open_training)
        self.back_button.place_forget()
        self.animation_running = True
        
        days_data = [
            ("Day 1", 100, [
                "1. Barbell Squats",
                "2. Bench Press",
                "3. Bent-over Rows",
                "4. Bicep Curls",
                "5. Crunches (Abs)"
            ]),
            ("Day 2", 1100, [
                "1. RDL (Hamstrings)",
                "2. Shoulder Press",
                "3. Lat Pulldown",
                "4. Lunges (Forward)",
                "5. Plank (40 sec)"
            ])
        ]
        
        for day_name, x_pos, exercises in days_data:
            day_label = tk.Label(self.window, text="", font=("ARIAL BLACK", 25), fg="#04b39e", bg=Config.BG_COLOR)
            day_label.place(x=x_pos, y=290)
            TextAnimator.animate(day_label, day_name)
            
            for i, exercise in enumerate(exercises):
                ex_label = tk.Label(self.window, text="", font=("Consolas", 20), fg="#6d45ff", bg=Config.BG_COLOR)
                ex_label.place(x=x_pos, y=350 + i * 40)
                TextAnimator.animate(ex_label, exercise)
                
        sets_reps = [
            (365, 345, "5×5"), (320, 385, "5×5"), (365, 425, "4×8"), (320, 465, "3x10"), (365, 505, "3x15"),
            (1395, 345, "4x10"), (1367, 385, "3x12"), (1335, 425, "3x10"), (1395, 465, "3x10per leg"), (1362, 505, "3x40sec")
        ]
        
        self.window.after(1000, lambda: self.show_sets_reps(sets_reps))
        
    def show_sets_reps(self, sets_reps):
        for x, y, text in sets_reps:
            sets_reps_label = tk.Label(self.window, text="", font=("ARIAL BLACK", 20), fg="#d4bf02", bg=Config.BG_COLOR)
            sets_reps_label.place(x=x, y=y)
            TextAnimator.animate(sets_reps_label, text)
        self.window.after(1000, lambda: self.back_button.place(x=0, y=0))
        
    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = Application()
    app.run()