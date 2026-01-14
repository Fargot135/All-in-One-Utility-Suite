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


window = ctk.CTk()
window.resizable(False, False)
window.title("PET-project")
window.geometry('1080x720')
window.configure(fg_color="#212121")

def vertical_text_button(text):
    return "\n".join(text)

canvas = tk.Canvas(window, width=1080, height=720, bg='#212121', bd=0, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

wave_speed = 1.2
wave_height = 50
wave_frequency = 80
wave_offset = 0
wave_base_y = 800

def rgb_to_hex(r, g, b):
    return f'#{int(r):02x}{int(g):02x}{int(b):02x}'

def draw_wave():
    global wave_offset
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    canvas.delete("wave")
    r = 127 + 127 * math.sin(wave_offset / 110)
    g = 127 + 127 * math.sin(wave_offset / 120 + 2)
    b = 127 + 127 * math.sin(wave_offset / 130 + 4)
    color1 = rgb_to_hex(r, g, b)
    dim_factor = 0.4
    color2 = rgb_to_hex(r * dim_factor, g * dim_factor, b * dim_factor)
    wave1 = {
        "color": color1,
        "height": wave_height * 0.8,
        "frequency": wave_frequency * 1.5,
        "offset": wave_offset,
    }
    wave2 = {
        "color": color2,
        "height": wave_height * 0.5,
        "frequency": wave_frequency * 2.5,
        "offset": wave_offset * 0.5,
    }
    def draw_single_wave(wave_data):
        points = []
        for x in range(0, 1660, 10):
            dyn_height = wave_data["height"] - 20 * math.sin(wave_data["offset"] / 30)
            y = wave_base_y + dyn_height * math.sin((x + wave_data["offset"]) / wave_data["frequency"])
            points.append(x)
            points.append(y)
        for i in range(0, len(points) - 2, 2):
            x1 = points[i]
            y1 = points[i + 1]
            x2 = points[i + 2]
            y2 = points[i + 3]
            canvas.create_polygon(x1, y1, x2, y2, x2, canvas_height, x1, canvas_height,
                                  fill=wave_data["color"], outline="", tags="wave")
    draw_single_wave(wave2)
    draw_single_wave(wave1)
    wave_offset += wave_speed
    window.after(16, draw_wave)

animation_running = False

def stop_animation():
    global animation_running
    animation_running = False

def animate_label(label, text, delay=50, index=0, callback=None):
    if index < len(text):
        label.config(text=text[:index + 1])
        window.after(delay, animate_label, label, text, delay, index + 1, callback)
    else:
        if callback:
            callback()

def animate_label_text(label, text, delay=50, callback=None):
    animate_label(label, text, delay, callback=callback)

BASE_DIR = os.path.dirname(__file__)


def get_path(filename):
    return os.path.join(BASE_DIR, "images", filename)

image_weather = Image.open(get_path("weather.png")).convert("RGBA")
image_idea = Image.open(get_path("cube.png")).convert("RGBA")
image_training = Image.open(get_path("dumbbell.png")).convert("RGBA")

image_resized_weather = image_weather.resize((100, 100), Image.Resampling.LANCZOS)
image_resized_idea = image_idea.resize((100, 100), Image.Resampling.LANCZOS)
image_resized_training = image_training.resize((100, 100), Image.Resampling.LANCZOS)

photo_weather = ImageTk.PhotoImage(image_resized_weather)
photo_idea = ImageTk.PhotoImage(image_resized_idea)
photo_training = ImageTk.PhotoImage(image_resized_training)

image_label = tk.Label(window, borderwidth=0, bg=window["bg"], highlightthickness=0)

x_offsets = {
    "weather": 65,
    "idea": 65,
    "training": 70
}

images = {
    "weather": photo_weather,
    "idea": photo_idea,
    "training": photo_training
}

animation_cancelled = False
animation_in_progress = False
animation_direction = None
is_image_shown = False

def animate_show(y_start, y_end, fixed_x, step=5):
    global animation_direction
    def move():
        nonlocal y_start
        if animation_cancelled:
            return
        if y_start > y_end:
            y_start -= step
            image_label.place(x=fixed_x, y=y_start)
            window.after(5, move)
        else:
            image_label.place(x=fixed_x, y=y_end)
            global animation_in_progress
            animation_in_progress = False
    move()
    animation_direction = 'up'

def is_mouse_over_button(btn, event):
    btn_x1 = btn.winfo_rootx()
    btn_y1 = btn.winfo_rooty()
    btn_x2 = btn_x1 + btn.winfo_width()
    btn_y2 = btn_y1 + btn.winfo_height()
    mouse_x = event.x_root
    mouse_y = event.y_root
    return btn_x1 <= mouse_x <= btn_x2 and btn_y1 <= mouse_y <= btn_y2

def show_image(event, image_key, btn):
    global animation_cancelled, animation_in_progress, is_image_shown
    if is_image_shown:
        return
    if not is_mouse_over_button(btn, event):
        return
    animation_cancelled = False
    animation_in_progress = True
    image_label.config(image=images[image_key])
    image_label.image = images[image_key]
    def place_image():
        btn_x = btn.winfo_rootx() - window.winfo_rootx()
        btn_y = btn.winfo_rooty() - window.winfo_rooty()
        x_offset = x_offsets[image_key]
        final_x = btn_x + x_offset
        start_y = btn_y
        end_y = 90
        image_label.place(x=final_x, y=start_y)
        animate_show(start_y, end_y, final_x)
    window.after(1, place_image)
    is_image_shown = True

def hide_image(event, btn):
    global animation_cancelled, animation_in_progress, animation_direction, is_image_shown
    if animation_in_progress:
        return
    if is_mouse_over_button(btn, event):
        return
    animation_cancelled = False
    animation_in_progress = True
    start_y = image_label.winfo_y()
    final_x = image_label.winfo_x()
    end_y = btn.winfo_y()
    animate_hide(start_y, end_y, final_x)
    is_image_shown = False

def animate_hide(y_start, y_end, fixed_x, step=5):
    global animation_direction
    def move():
        nonlocal y_start
        if animation_cancelled:
            return
        if y_start < y_end:
            y_start += step
            image_label.place(x=fixed_x, y=y_start)
            window.after(5, move)
        else:
            image_label.place_forget()
            window.update_idletasks()
            global animation_in_progress
            animation_in_progress = False
    move()
    animation_direction = 'down'

def AddIdea():
    Value = EnterText.get("1.0", "end-1c")
    if Value != '':
        with open('How.txt', 'a+', encoding="utf-8") as file:
            file.write(Value + '\n')
        EnterText.delete("1.0", "end")
    else:
        tk.messagebox.showinfo("Error", "The input field is blank")

def RandomIdea():
    with open('How.txt', 'r', encoding="utf-8") as file:
        Lines = file.readlines()
        if Lines:
            tk.messagebox.showinfo("Randomiser", choice(Lines))
        else:
            tk.messagebox.showinfo("Randomiser", "File empty")

idea_label = tk.Label(window, text="Enter the option", font=("WIDE LATIN", 30), fg="#ffa800", bg='#212121')
EnterText = tk.Text(
    window,
    font=("Arial", 20),
    width=50,
    height=2,
    fg="#ffa800",
    bg="#19015c",
    bd=0,
    highlightthickness=8,
    highlightbackground="#ffa800",
    highlightcolor="#ffa800"
)
btn_add = ctk.CTkButton(
    window,
    text=("Add a variant"),
    font=ctk.CTkFont("Consolas", 25),
    fg_color="#7c827d",
    text_color="#212121",
    hover_color="#19015c",
    corner_radius=15,
    command=AddIdea,
    width=100,
    height=50
)
btn_show = ctk.CTkButton(
    window,
    text=("Random selection"),
    font=ctk.CTkFont("Consolas", 25),
    fg_color="#7c827d",
    text_color="#212121",
    hover_color="#1dd75a",
    corner_radius=15,
    command=RandomIdea,
    width=100,
    height=50
)

def OpenIdeaWindow():
    clear_window()
    back_button.config(command=back_to_main)
    back_button.place(x=0, y=0)
    idea_label.place(x=525, y=80)
    EnterText.place(x=410, y=200)
    btn_add.place(x=273, y=210)
    btn_show.place(x=530, y=210)
    def EnterClick(event):
        AddIdea()
    EnterText.bind('<Return>', EnterClick)

def GetWeather():
    clear_window()
    weather_label = tk.Label(window, text="Enter city name:", font=("WIDE LATIN", 30), bg='#212121', fg="#ffa800")
    weather_label.place(x=525, y=80)
    city_entry = tk.Text(
        window,
        font=("Arial", 20),
        width=50,
        height=2,
        fg="#ffa800",
        bg="#02325e",
        bd=0,
        highlightthickness=8,
        highlightbackground="#ffa800",
        highlightcolor="#ffa800"
    )
    city_entry.place(x=410, y=200)
    submit_button = ctk.CTkButton(
        window,
        text="Get Weather",
        font=ctk.CTkFont("Consolas", 25),
        fg_color="#7c827d",
        text_color="#212121",
        hover_color="#02325e",
        corner_radius=15,
        command=GetWeather,
        width=300,
        height=70
    )
    submit_button.place(x=375, y=250)
    def fetch_weather():
        city = city_entry.get("1.0", "end-1c").strip()
        if city:
            try:
                city_encoded = urllib.parse.quote(city)
                api_key = "YOUR_API_KEY_HERE"
                url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_encoded}&appid={api_key}&units=metric&lang=en"
                response = requests.get(url)
                data = response.json()
                if data["cod"] == "200":
                    current_data = data["list"][0]
                    current_temp = current_data["main"]["temp"]
                    current_condition = current_data["weather"][0]["description"]
                    current_humidity = current_data["main"]["humidity"]
                    current_wind = current_data["wind"]["speed"]
                    icon_code = current_data["weather"][0]["icon"]
                    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                    icon_response = requests.get(icon_url)
                    icon_image = Image.open(BytesIO(icon_response.content))
                    icon_image = icon_image.resize((160, 160))
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    weather_window = tk.Toplevel()
                    weather_window.title(f"Weather forecast for {city}")
                    weather_window.geometry("720x1080")
                    weather_window.configure(bg='#e0f7fa')
                    city_label = tk.Label(weather_window, text=f"Weather in {city}", font=("Arial", 28, "bold"),
                                          bg='#e0f7fa')
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
                    current_info_label = tk.Label(weather_window, text=current_info_text, font=("Arial", 16),
                                                  bg='#e0f7fa', justify='left')
                    current_info_label.pack(pady=30)
                    forecast_label = tk.Label(weather_window, text="3-day Forecast:", font=("Arial", 20, "bold"),
                                              bg='#e0f7fa')
                    forecast_label.pack(pady=30)
                    for i in range(1, 4):
                        forecast_data = data["list"][i * 8]
                        forecast_temp = forecast_data["main"]["temp"]
                        forecast_condition = forecast_data["weather"][0]["description"]
                        forecast_icon_code = forecast_data["weather"][0]["icon"]
                        forecast_icon_url = f"http://openweathermap.org/img/wn/{forecast_icon_code}@2x.png"
                        forecast_icon_response = requests.get(forecast_icon_url)
                        forecast_icon_image = Image.open(BytesIO(forecast_icon_response.content))
                        forecast_icon_image = forecast_icon_image.resize((100, 100))
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
                        forecast_text_label = tk.Label(forecast_frame, text=forecast_info_text, font=("Arial", 14),
                                                       bg='#e0f7fa', justify='left')
                        forecast_text_label.pack(side="left", padx=15)
                    close_button = tk.Button(weather_window, text="Close", command=weather_window.destroy,
                                             font=("Arial", 16))
                    close_button.pack(pady=30)
                else:
                    messagebox.showinfo("Error", "City not found.")
            except Exception as e:
                messagebox.showinfo("Error", f"Failed to retrieve weather: {e}")
        else:
            messagebox.showinfo("Error", "The input field is empty.")
    submit_button.configure(command=fetch_weather)
    city_entry.bind('<Return>', lambda event: fetch_weather())
    back_button.place(x=0, y=0)

def back_to_main():
    stop_animation()
    clear_window()
    back_button.place_forget()

def clear_window():
    for widget in window.winfo_children():
        widget.place_forget()

def back_to_training():
    stop_animation()
    clear_window()
    OpenTrainingWindow()

def OpenTrainingWindow():
    clear_window()
    stop_animation()
    training_label = tk.Label(window, text="Select a training program", font=("WIDE LATIN", 30), fg="#ffa800",
                              bg='#212121')
    training_label.place(x=390, y=80)
    btn_split = ctk.CTkButton(
        window,
        text=vertical_text_button("split"),
        command=show_split_program,
        width=150,
        height=360,
        corner_radius=15,
        text_color="#212121",
        font=ctk.CTkFont("Consolas", 25),
        fg_color="#7c827d",
        hover_color="#c41b1b"
    )
    btn_split.place(x=157.5, y=127)
    btn_full_body = ctk.CTkButton(
        window,
        text=vertical_text_button("Full body"),
        command=show_full_body_program,
        width=150,
        height=360,
        corner_radius=15,
        text_color="#212121",
        font=ctk.CTkFont("Consolas", 25),
        fg_color="#7c827d",
        hover_color="#026e06"
    )
    btn_full_body.place(x=465, y=127)
    btn_upper_lower = ctk.CTkButton(
        window,
        text=vertical_text_button("Upper/Lower"),
        command=show_upper_lower_program,
        width=150,
        height=360,
        corner_radius=15,
        text_color="#212121",
        font=ctk.CTkFont("Consolas", 25),
        fg_color="#7c827d",
        hover_color="#0642cc"
    )
    btn_upper_lower.place(x=772.5, y=127)
    back_button.config(command=back_to_main)
    back_button.place(x=0, y=0)
    btn_split.place(x=157.5, y=127)
    btn_full_body.place(x=465, y=127)
    btn_upper_lower.place(x=772.5, y=127)

def animate_split_exercises_day_1():
    ex1_texts = [
        "1. Bench Press",
        "2. Incline Dumbbell Press",
        "3. Dips",
        "4. Dumbbell Flyes",
        "5. Tricep Pushdowns"
    ]
    for i, txt in enumerate(ex1_texts):
        ex1_label = tk.Label(window, text="", font=("Consolas", 20), fg="#6d45ff", bg='#212121')
        ex1_label.place(x=100, y=350 + i * 40)
        animate_label_text(ex1_label, txt)

def animate_split_exercises_day_2():
    ex2_texts = [
        "1. Pull-ups",
        "2. Barbell Rows",
        "3. Lat Pulldown",
        "4. Dumbbell Rows",
        "5. Barbell Curls"
    ]
    for i, txt in enumerate(ex2_texts):
        ex2_label = tk.Label(window, text="", font=("Consolas", 20), fg="#6d45ff", bg='#212121')
        ex2_label.place(x=650, y=350 + i * 40)
        animate_label_text(ex2_label, txt)

def animate_split_exercises_day_3():
    ex3_texts = [
        "1. Barbell Squats",
        "2. Leg Press",
        "3. Romanian Deadlifts",
        "4. Seated Shoulder Press",
        "5. Lateral Raises"
    ]
    for i, txt in enumerate(ex3_texts):
        ex3_label = tk.Label(window, text="", font=("Consolas", 20), fg="#6d45ff", bg='#212121')
        ex3_label.place(x=1100, y=350 + i * 40)
        animate_label_text(ex3_label, txt)

def show_split_program():
    clear_window()
    stop_animation()
    label = tk.Label(window, text="Split Training Program", font=("WIDE LATIN", 35), fg="#c41b1b", bg='#212121')
    label.place(x=335, y=80)
    back_button.config(command=back_to_training)
    back_button.place_forget()
    global animation_running
    animation_running = True
    create_split_days_and_exercises()

def create_split_days_and_exercises():
    day_1_label = tk.Label(window, text="", font=("ARIAL BLACK", 25), fg="#04b39e", bg='#212121')
    day_1_label.place(x=100, y=290)
    animate_label_text(day_1_label, "Day 1")
    day_2_label = tk.Label(window, text="", font=("ARIAL BLACK", 25), fg="#04b39e", bg='#212121')
    day_2_label.place(x=650, y=290)
    animate_label_text(day_2_label, "Day 2")
    day_3_label = tk.Label(window, text="", font=("ARIAL BLACK", 25), fg="#04b39e", bg='#212121')
    day_3_label.place(x=1100, y=290)
    animate_label_text(day_3_label, "Day 3")
    animate_split_exercises_day_1()
    animate_split_exercises_day_2()
    animate_split_exercises_day_3()
    window.after(1000, show_sets_reps)

def show_sets_reps():
    sets_reps = [
        (320, 345, "4x8"), (485, 385, "4x10"), (215, 425, "3x10"), (365, 465, "3x12"), (395, 505, "3x12"),
        (825, 345, "4x8"), (890, 385, "4x10"), (890, 425, "3x10"), (900, 465, "3x12"), (900, 505, "3x12"),
        (1370, 345, "4x8"), (1297, 385, "4x10"), (1430, 425, "3x10"), (1475, 465, "4x8"), (1370, 505, "3x15")
    ]
    for x, y, text in sets_reps:
        sets_reps_label = tk.Label(window, text="", font=("ARIAL BLACK", 20), fg="#d4bf02", bg='#212121')
        sets_reps_label.place(x=x, y=y)
        animate_label_text(sets_reps_label, text)
    window.after(1000, show_back_button)

def show_back_button():
    back_button.place(x=0, y=0)

def animate_full_body_day_1():
    ex1_texts = [
        "1. Barbell Squats",
        "2. Bench Press",
        "3. Bent-over Rows",
        "4. Bicep Curls",
        "5. Crunches (Abs)"
    ]
    for i, txt in enumerate(ex1_texts):
        ex1_label = tk.Label(window, text="", font=("Consolas", 20), fg="#6d45ff", bg='#212121')
        ex1_label.place(x=100, y=350 + i * 40)
        animate_label_text(ex1_label, txt)

def animate_full_body_day_2():
    ex2_texts = [
        "1. Romanian Deadlifts",
        "2. Shoulder Press",
        "3. Lat Pulldown",
        "4. Forward Lunges",
        "5. Plank (40 seconds)"
    ]
    for i, txt in enumerate(ex2_texts):
        ex2_label = tk.Label(window, text="", font=("Consolas", 20), fg="#6d45ff", bg='#212121')
        ex2_label.place(x=650, y=350 + i * 40)
        animate_label_text(ex2_label, txt)

def animate_full_body_day_3():
    ex3_texts = [
        "1. Leg Press",
        "2. Dumbbell Bench Press",
        "3. One-Arm Dumbbell Row",
        "4. Bicep Curls + Triceps Ext",
        "5. Crunches (Abs)"
    ]
    for i, txt in enumerate(ex3_texts):
        ex3_label = tk.Label(window, text="", font=("Consolas", 20), fg="#6d45ff", bg='#212121')
        ex3_label.place(x=1100, y=350 + i * 40)
        animate_label_text(ex3_label, txt)

def show_full_body_program():
    clear_window()
    stop_animation()
    label = tk.Label(window, text="Full Body Program", font=("WIDE LATIN", 35), fg="#026e06", bg='#212121')
    label.place(x=385, y=80)
    back_button.config(command=back_to_training)
    back_button.place_forget()
    global animation_running
    animation_running = True
    create_full_body_days_and_exercises()

def create_full_body_days_and_exercises():
    day_1_label = tk.Label(window, text="", font=("ARIAL BLACK", 25), fg="#04b39e", bg='#212121')
    day_1_label.place(x=100, y=290)
    animate_label_text(day_1_label, "Day 1")
    day_2_label = tk.Label(window, text="", font=("ARIAL BLACK", 25), fg="#04b39e", bg='#212121')
    day_2_label.place(x=650, y=290)
    animate_label_text(day_2_label, "Day 2")
    day_3_label = tk.Label(window, text="", font=("ARIAL BLACK", 25), fg="#04b39e", bg='#212121')
    day_3_label.place(x=1100, y=290)
    animate_label_text(day_3_label, "Day 3")
    animate_full_body_day_1()
    animate_full_body_day_2()
    animate_full_body_day_3()
    window.after(1000, show_full_body_sets_reps)

def show_full_body_sets_reps():
    sets_reps = [
        (365, 345, "5×5"), (320, 385, "5×5"), (365, 425, "4×8"), (320, 465, "3x10"), (365, 505, "3x15"),
        (975, 345, "4x10"), (915, 385, "3x12"), (885, 425, "3x10"), (920, 465, "3x10per leg"), (970, 505, "3x40sec"),
        (1290, 345, "4x12"), (1370, 385, "4x10"), (1455, 425, "4x10"), (1535, 465, "3x12"), (1362, 505, "3x20")
    ]
    for x, y, text in sets_reps:
        sets_reps_label = tk.Label(window, text="", font=("ARIAL BLACK", 20), fg="#d4bf02", bg='#212121')
        sets_reps_label.place(x=x, y=y)
        animate_label_text(sets_reps_label, text)
    window.after(1000, show_back_button)

def animate_upper_lower_day_1():
    ex1_texts = [
        "1. Barbell Squats",
        "2. Bench Press",
        "3. Bent-over Rows",
        "4. Bicep Curls",
        "5. Crunches (Abs)"
    ]
    for i, txt in enumerate(ex1_texts):
        ex1_label = tk.Label(window, text="", font=("Consolas", 20), fg="#6d45ff", bg='#212121')
        ex1_label.place(x=100, y=350 + i * 40)
        animate_label_text(ex1_label, txt)

def animate_upper_lower_day_2():
    ex2_texts = [
        "1. RDL (Hamstrings)",
        "2. Shoulder Press",
        "3. Lat Pulldown",
        "4. Lunges (Forward)",
        "5. Plank (40 sec)"
    ]
    for i, txt in enumerate(ex2_texts):
        ex2_label = tk.Label(window, text="", font=("Consolas", 20), fg="#6d45ff", bg='#212121')
        ex2_label.place(x=1100, y=350 + i * 40)
        animate_label_text(ex2_label, txt)

def show_upper_lower_program():
    clear_window()
    stop_animation()
    label = tk.Label(window, text="Upper/Lower Program", font=("WIDE LATIN", 35), fg="#0642cc", bg='#212121')
    label.place(x=335, y=80)
    back_button.config(command=back_to_training)
    back_button.place_forget()
    global animation_running
    animation_running = True
    create_upper_lower_days_and_exercises()

def create_upper_lower_days_and_exercises():
    day_1_label = tk.Label(window, text="", font=("ARIAL BLACK", 25), fg="#04b39e", bg='#212121')
    day_1_label.place(x=100, y=290)
    animate_label_text(day_1_label, "Day 1")
    day_2_label = tk.Label(window, text="", font=("ARIAL BLACK", 25), fg="#04b39e", bg='#212121')
    day_2_label.place(x=1100, y=290)
    animate_label_text(day_2_label, "Day 2")
    animate_upper_lower_day_1()
    animate_upper_lower_day_2()
    window.after(1000, show_upper_lower_sets_reps)

def show_upper_lower_sets_reps():
    sets_reps = [
        (365, 345, "5×5"), (320, 385, "5×5"), (365, 425, "4×8"), (320, 465, "3x10"), (365, 505, "3x15"),
        (1395, 345, "4x10"), (1367, 385, "3x12"), (1335, 425, "3x10"), (1395, 465, "3x10per leg"), (1362, 505, "3x40sec")
    ]
    for x, y, text in sets_reps:
        sets_reps_label = tk.Label(window, text="", font=("ARIAL BLACK", 20), fg="#d4bf02", bg='#212121')
        sets_reps_label.place(x=x, y=y)
        animate_label_text(sets_reps_label, text)
    window.after(1000, show_back_button)

def back_to_idea():
    OpenIdeaWindow()

main_label = tk.Label(window, text="CHOOSE A FUNCTION:", font=("WIDE LATIN", 25), fg="#ffa800", bg='#212121')

btn_weather = ctk.CTkButton(
    window,
    text=vertical_text_button("weather"),
    font=ctk.CTkFont("Consolas", 25),
    fg_color="#7c827d",
    text_color="#212121",
    hover_color="#57f7f2",
    corner_radius=15,
    command=GetWeather,
    width=150, height=360
)
btn_weather.place(x=157.5, y=127)

btn_idea = ctk.CTkButton(
    window,
    text=vertical_text_button("randomiser"),
    font=ctk.CTkFont("Consolas", 25),
    fg_color="#7c827d",
    text_color="#212121",
    hover_color="#6d1ae6",
    corner_radius=15,
    command=OpenIdeaWindow,
    width=150, height=360
)
btn_idea.place(x=465, y=127)

btn_training = ctk.CTkButton(
    window,
    text=vertical_text_button("training"),
    font=ctk.CTkFont("Consolas", 25),
    fg_color="#7c827d",
    text_color="#212121",
    hover_color="#1dd75a",
    corner_radius=15,
    command=OpenTrainingWindow,
    width=150, height=360
)
btn_training.place(x=772.5, y=127)

def back_to_main():
    clear_window()
    main_label.place(x=460, y=50)
    btn_weather.place(x=157.5, y=127)
    btn_idea.place(x=465, y=127)
    btn_training.place(x=772.5, y=127)

back_button = tk.Button(window, text="←BACK", font=("ARIAL BLACK", 15), command=back_to_main, bg='#ff3600', fg='white')

main_label.place(x=460, y=50)

btn_weather.bind("<Enter>", lambda event: show_image(event, "weather", btn_weather))
btn_weather.bind("<Leave>", lambda event: hide_image(event, btn_weather))

btn_idea.bind("<Enter>", lambda event: show_image(event, "idea", btn_idea))
btn_idea.bind("<Leave>", lambda event: hide_image(event, btn_idea))

btn_training.bind("<Enter>", lambda event: show_image(event, "training", btn_training))
btn_training.bind("<Leave>", lambda event: hide_image(event, btn_training))

draw_wave()

window.mainloop()