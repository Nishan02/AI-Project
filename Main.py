import tkinter
from tkinter import *
import customtkinter as ctk
from PIL import ImageTk ,Image
import cv2
from fireDetection import fire_detection as fire
import flags
import hashlib  
from tkinter import messagebox 
import json
import re

user_credentials = {}

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def register_user():
    name = entry1.get()
    email = entry2.get()
    password = entry3.get()
    
    if not name or not email or not password:
        messagebox.showerror("Error", "Please fill in all fields.")
        return
    
    if not is_valid_email(email):
        messagebox.showerror("Error", "Please enter a valid email address.")
        return
    
    if email in [email for email,_ in user_credentials.items()]:
        messagebox.showerror("Error", "This email is already registered.")
        return
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    user_credentials[email] = hashed_password

    save_user_credentials()
    
    entry1.delete(0, 'end')
    entry2.delete(0, 'end')
    entry3.delete(0, 'end')

    messagebox.showinfo("Registration Successful", "You have been successfully registered!")

def save_user_credentials():
    with open('user_credentials.json', 'w') as file:
        json.dump(user_credentials, file)

def load_user_credentials():
    try:
        with open('user_credentials.json', 'r') as file:
            user_credentials.update(json.load(file))
    except FileNotFoundError:
        pass  
    
ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("green")

load_user_credentials()

app1 = ctk.CTk()  #creating cutstom tkinter window
app1.geometry("600x440")
app1.title('Login')

def main_page():
    name = entry1.get()     
    email = entry2.get()
    password = entry3.get()
    flags.name = name       
    flags.email = email
    
    if not name or not email or not password:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    if email in user_credentials:
        if user_credentials[email] == hashed_password:
            messagebox.showinfo("Login Successful", "Welcome back, " + name + "!")
        else:
            messagebox.showerror("Login Failed", "Incorrect password. Please try again.")
            return 
    else:
        messagebox.showerror("Login Failed", "User not found. Please register.")
        return 

    app1.destroy()            # destroy current window and creating new one 
    window = ctk.CTk()
    window.geometry("1280x720")
    window.title("Smart CCTV")
    app = Frame(window)
    app.grid()
    lmain = Label(app)
    lmain.grid()
    info_label = Label(window, text="Activity", font=("Georgia", 15), bg="#262626", fg="white")
    info_label.place(relx=1, rely=0.1, anchor="ne", width=300)

    def update_info_label():
        text = "\n\n"  
        if flags.fire_email:
            text += "Fire Alert!!!!\n\n"

        info_label.configure(text=text)
        info_label.after(100, update_info_label)

    def reset_flags():
        flags.prohibited_email = False
        flags.restricted_email = False
        flags.fire_email = False
        flags.accident_email = False
        flags.started = False

    class SlidePanel(ctk.CTkFrame):
        def __init__(self,parent,start_pos,end_pos):
            super().__init__(master = parent)
            self.start_pos = start_pos +0.04
            self.end_pos = end_pos -0.02
            self.width = abs(start_pos - end_pos)
            self.pos = self.start_pos
            self.in_start_pos = True
            self.place(relx=self.start_pos,rely=0.05,relwidth=self.width,relheight=0.9)

        def animate(self):
            if self.in_start_pos:
                self.animate_forward()
            else:
                self.animate_backward()
        def animate_forward(self):
            if self.pos > self.end_pos:
                self.pos -= 0.008
                self.place(relx=self.pos,rely=0.05,relwidth=self.width,relheight=0.9)
                self.after(10,self.animate_forward)
            else:
                self.in_start_pos = False
        def animate_backward(self):
            if self.pos < self.start_pos:
                self.pos += 0.008
                self.place(relx=self.pos,rely=0.05,relwidth=self.width,relheight=0.9)
                self.after(10,self.animate_backward)
            else:
                self.in_start_pos = True

    cap = cv2.VideoCapture(0)
    width, height = 1300, 620
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    class streamer:
        is_running = False
        def video_stream():
            ret, frame = cap.read()
            if is_running and ret:
                # if switch_var_1.get() == "on":
                #     face(frame)
                if switch_var_2.get() == "on":
                    fire(frame)
                    
                photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                lmain.photo = photo
                lmain.configure(image=photo)
                lmain.after(10, streamer.video_stream)
        def start():
            global is_running
            is_running = True
            streamer.video_stream()
        def stop():
            global is_running
            is_running = False
            streamer.video_stream()

    animated_panel = SlidePanel(window, 1.0, 0.85)
    switch_var_2 = ctk.StringVar(value="off")

    ctk.CTkLabel(animated_panel, text="Select Features").pack(padx=20,pady=20)
    
    switch_2 = ctk.CTkSwitch(animated_panel, text="Fire and Smoke      \nDetection",font=("arial",13), variable=switch_var_2,onvalue="on",offvalue="off")
    switch_2.pack(padx=20,pady=10)
    

    ctk.CTkButton(animated_panel, text="Refresh", command=reset_flags).pack(padx=20,pady=20)

    button_1 = ctk.CTkButton(window, text="Features Tab", width=170,height=33,corner_radius=25,font=("cosmic sans ms",15),fg_color="#2d71bf",hover_color="#48abab",command=animated_panel.animate)
    button_1.place(relx=0.7,rely=0.87,anchor="n")
    
    btn_start = ctk.CTkButton(window, text="START", width=100,height=33,corner_radius=25,font=("cosmic sans ms",14),fg_color="#2d71bf",hover_color="#48abab", command=streamer.start)
    btn_start.place(relx=0.15,rely=0.87,anchor="n")
    
    btn_stop = ctk.CTkButton(window, text="STOP", width=100,height=33,corner_radius=25,font=("cosmic sans ms",14),fg_color="#2d71bf",hover_color="#48abab", command=streamer.stop)
    btn_stop.place(relx=0.23,rely=0.87,anchor="n")
    
    gen_button = ctk.CTkButton(window, text="Generate Report", width=130,height=33,corner_radius=25,font=("cosmic sans ms",14),fg_color="#2d71bf",hover_color="#48abab", command=flags.gen_report)
    gen_button.place(relx=0.42,rely=0.87,anchor="n")

    update_info_label()
    window.mainloop()
    


img1=ImageTk.PhotoImage(Image.open("assets/bg_img/pattern.png"))

l1=ctk.CTkLabel(master=app1,image=img1)
l1.pack()

frame=ctk.CTkFrame(master=l1, width=320, height=420, corner_radius=15)
frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

l2 = ctk.CTkLabel(master=frame, text="Register or Login", font=('Century Gothic', 20))
l2.place(x=50, y=45)

entry1 = ctk.CTkEntry(master=frame, width=220, placeholder_text='Enter your Name')
entry1.place(x=50, y=100)
entry2 = ctk.CTkEntry(master=frame, width=220, placeholder_text='Email')
entry2.place(x=50, y=150)
entry3 = ctk.CTkEntry(master=frame, width=220, placeholder_text='Password', show='*')
entry3.place(x=50, y=200)

l3 = ctk.CTkLabel(master=frame, text="New user? Register here:", font=('Century Gothic', 12))
l3.place(x=50, y=250)

register_button = ctk.CTkButton(master=frame, width=220, text="Register", command=register_user, corner_radius=6)
register_button.place(x=50, y=300)

login_button = ctk.CTkButton(master=frame, width=220, text="Login", command=main_page, corner_radius=6)
login_button.place(x=50, y=350)

app1.mainloop()
