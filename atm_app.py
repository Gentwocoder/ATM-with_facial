from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from backend import backend
import tkinter as tk
import numpy as np
import sqlite3
import bcrypt
import cv2


ch = backend
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# encryption_key = b'AZ1R22KVI5JwkEL188WlUqNxkn_YYLnbn6hJ8YnQdV8='
# cipher = Fernet(encryption_key)

current_user = {}


class Signin(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#F0F0F0")

        # Function to capture the user's face for verification
        def capture_for_verification():
            cam = cv2.VideoCapture(0)
            face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            
            while True:
                ret, frame = cam.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    face = gray[y:y + h, x:x + w]
                    cam.release()
                    cv2.destroyAllWindows()
                    return face

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        # Compare the captured face with the stored face binary blob
        def compare_faces(stored_face_blob):
            # Convert stored binary blob to image
            face_array = np.frombuffer(stored_face_blob, dtype=np.uint8)
            stored_face = cv2.imdecode(face_array, cv2.IMREAD_GRAYSCALE)

            captured_face = capture_for_verification()

            # Resize and compare the faces
            stored_face_resized = cv2.resize(stored_face, (captured_face.shape[1], captured_face.shape[0]))
            
            difference = cv2.absdiff(stored_face_resized, captured_face)
            result = not np.any(difference)  # If there is no difference, the faces match
            
            return result

        # Function to fetch user details after successful login
        def login_user(fullname, password):
            # Fetch user details
            cursor.execute("SELECT password, face_enrolled FROM user WHERE account_holder = ?", (fullname,))
            result = cursor.fetchone()

            conn.close()

            if result:
                stored_password, face_blob = result

                if bcrypt.checkpw(password.encode("utf-8"), stored_password):
                    if compare_faces(face_blob):
                        # Split fullname to get the first name
                        first_name = fullname.split(" ")[0]
                        # Store the logged-in user details in a global dictionary
                        current_user['first_name'] = first_name
                        current_user['full_name'] = fullname
                        # controller.show_frame(Mainpage)
                        messagebox.showinfo("Success", "Logged in Sucessfully!!")
                        return True
                    else:
                        messagebox.showerror("Error", "Face Verification failed")
                        return False
                else:
                    messagebox.showerror("Error", "Invalid Password!!")
            else:
                messagebox.showerror("Error", "User not found")
                return False

        def signin():
            get_name = name_entry.get()
            get_password = password_entry.get()
            if len(get_password) != 0 and len(get_name) != 0:
                if login_user(get_name, get_password):
                    first_name = current_user.get('first_name', '')
                    messagebox.showinfo("Login Successful", f"Welcome, {first_name}!")
                    controller.show_frame(Mainpage)
                else:
                    messagebox.showerror("Login Failed", "Invalid name or password.")
            else:
                messagebox.showerror(title="Error", message="No space should be left blank!!")

        load_img = Image.open("images/signup-img.png")
        img = ImageTk.PhotoImage(load_img)
        label_1 = tk.Label(self, image=img, border=0)
        label_1.image=img
        label_1.place(x=50, y=50)

        frame = tk.Frame(self, width=350, height=350, bg="#F0F0F0")
        frame.place(x=480, y=70)

        heading = tk.Label(frame, text="sign in", fg="#C53F3F", bg="#F0F0F0", font=("Microsoft YaHei UI Light", 23, "bold"))
        heading.place(x=100, y=5)

        def on_enter(e):
            name_entry.delete(0, END)

        def on_leave(e):
            user = name_entry.get()
            if user == "":
                name_entry.insert(0, "Enter full name")
            
        name_entry = tk.Entry(frame, width=25, fg="black", border=0, bg="#F0F0F0", font=("Microsoft YaHei UI Light", 11))
        name_entry.place(x=30, y=80)
        name_entry.insert(0, "Enter full name")

        name_entry.bind("<FocusIn>", on_enter)
        name_entry.bind("<FocusOut>", on_leave)


        tk.Frame(frame, width=295, height=2, bg="black").place(x=25, y=107)

        def on_enter(e):
            password_entry.delete(0, END)
            password_entry.configure(show="*")

        def on_leave(e):
            pw = password_entry.get()
            if pw == "":
                password_entry.insert(0, "Enter password")

        password_entry = tk.Entry(frame, width=25, fg="black", border=0, bg="#F0F0F0", font=("Microsoft YaHei UI Light", 11))
        password_entry.place(x=30, y=150)
        password_entry.insert(0, "Enter password")


        password_entry.bind("<FocusIn>", on_enter)
        password_entry.bind("<FocusOut>", on_leave)


        tk.Frame(frame, width=295, height=2, bg="black").place(x=25, y=177)

        tk.Button(frame, width=39, pady=7, text="Enter", bg="#C53F3F", fg="white", border=0, command=signin).place(x=35, y=204)
        label = tk.Label(frame, text="Don't have an account?", fg="black", bg="#F0F0F0", font=("Microsoft YaHei UI Light", 9))
        label.place(x=75, y=270)

        sign_up = tk.Button(frame, width=9, text="Sign up", border=0, bg="#F0F0F0", cursor="hand2", fg="#C53F3F", command=lambda: controller.show_frame(Signup))
        sign_up.place(x=215, y=265)


class Signup(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#fff")
        balance = 0.0

        def capture_face():
            cap = cv2.VideoCapture(0)
            face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
            # tk.Label(text="Capturing face look at the camera")

            while True:
                ret, frame = cap.read()
                # Convert the image from BGR (OpenCV format) to GRAY (black and white)
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    face = gray_frame[y:y + h, x:x + w]

                cv2.imshow('Capturing Face', frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            cap.release()
            cv2.destroyAllWindows()

            _, buffer = cv2.imencode(".jpg", face)
            face_blob = buffer.tobytes()

            return face_blob

        def register():
            get_firstname = first_name.get()
            get_lastname = last_name.get()
            get_password = password_entry.get()
            get_password2 = confirm_password.get()
            fullname = get_firstname + " " + get_lastname
            
            if len(get_firstname) != 0 and len(get_lastname) != 0 and len(get_password) !=0 and len(get_password2) !=0:              
                if get_password != get_password2:
                    messagebox.showerror(title="Error", message="Passwords do not match.")
                else:
                    encoded_password = get_password.encode("utf-8")
                    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
                    face_blob = capture_face()
                    ch.create_user(self, fullname, hashed_password, balance, face_blob)
                    first_name.delete(0, END)
                    last_name.delete(0, END)
                    password_entry.delete(0, END)
                    confirm_password.delete(0, END)
                    first_name.focus()
                    messagebox.showinfo(title="Successful", message="User Created Successfully!!")
                    controller.show_frame(Signin)
            else:
                messagebox.showerror(title="Error", message="No blank spaces!!")
        ## window image
        load_img = Image.open("images/signin.png")
        img = ImageTk.PhotoImage(load_img)
        label_1 = tk.Label(self, image=img, border=0, bg="white")
        label_1.image=img
        label_1.place(x=50, y=50)

        frame = tk.Frame(self, width=350, height=400, bg="white")
        frame.place(x=480, y=40)

        heading = tk.Label(frame, text="sign up for atm", fg="#C53F3F", bg="white", font=("Microsoft YaHei UI Light", 23, "bold"))
        heading.place(x=50, y=2)
        ## first name entry
        def on_enter(e):
            first_name.delete(0, END)
        first_name = tk.Entry(frame, width=25, fg="black", border=0, bg="white", font=("Microsoft YaHei UI Light", 11))
        first_name.place(x=30, y=50)
        first_name.insert(0, "Enter first name")

        first_name.bind("<FocusIn>", on_enter)

        tk.Frame(frame, width=295, height=2, bg="black").place(x=25, y=77)

        def on_enter_lastname(e):
            last_name.delete(0, END)

        last_name = tk.Entry(frame, width=25, fg="black", border=0, bg="white", font=("Microsoft YaHei UI Light", 11))
        last_name.place(x=30, y=120)
        last_name.insert(0, "Enter last name")

        on_enter_lastname("<FocusIn>", on_enter_lastname)

        tk.Frame(frame, width=295, height=2, bg="black").place(x=25, y=147)

        def on_enter_password(e):
            password_entry.delete(0, END)

        password_entry = tk.Entry(frame, width=25, fg="black", border=0, bg="white", font=("Microsoft YaHei UI Light", 11))
        password_entry.place(x=30, y=190)
        password_entry.insert(0, "Enter password")
        password_entry.configure(show="*")

        password_entry.bind("<FocusIn>", on_enter_password)

        tk.Frame(frame, width=295, height=2, bg="black").place(x=25, y=217)

        confirm_password = tk.Entry(frame, width=25, fg="black", border=0, bg="white", font=("Microsoft YaHei UI Light", 11))
        confirm_password.place(x=30, y=260)
        confirm_password.insert(0, "Confirm password")

        tk.Frame(frame, width=295, height=2, bg="black").place(x=25, y=287)

        tk.Button(frame, width=39, pady=7, text="Sign up", bg="#C53F3F", fg="white", border=0, command=register).place(x=32, y=320)
        label = tk.Label(frame, text="I have an account", fg="black", bg="white", font=("Microsoft YaHei UI Light", 9))
        label.place(x=90, y=370)

        signin = tk.Button(frame, width=6, text="Sign in", border=0, bg="white", cursor="hand2", fg="#C53F3F", command=lambda: controller.show_frame(Signin))
        signin.place(x=200, y=370)


class Mainpage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#fff")

        def deposit():
            window = tk.Toplevel(self)
            window.title("Deposit")
            window.geometry("300x300+300+200")
            window.resizable(False, False)

            amount_entry = tk.Entry(window, width=25, fg="black", border=0, bg="white", font=("Microsoft YaHei UI Light", 11))
            amount_entry.place(x=30, y=100)
            amount_entry.insert(0, "Enter amount")

            fullname = current_user.get("full_name")
            def complete_deposit():
                def get_current_balance():
                    cursor.execute("SELECT account_balance FROM user WHERE account_holder=?", (fullname,))
                    result = cursor.fetchone()

                    if result:
                        return result[0]

                try:
                    get_amount = float(amount_entry.get())
                    ch.update_balance(self, fullname, get_current_balance(), get_amount)
                    messagebox.showinfo("Success", "Deposited successfully")
                except:
                    messagebox.showinfo("Success", "Successful")
                    window.destroy()

            tk.Button(window, text="Deposit", width=25, bg="blue", fg="black", command=complete_deposit).place(x=25, y=220)

            window.mainloop()

        def withdraw():
            window = tk.Toplevel(self)
            window.title("Withdraw")
            window.geometry("300x300+300+200")
            window.resizable(False, False)

            amount_entry = tk.Entry(window, width=25, fg="black", border=0, bg="white", font=("Microsoft YaHei UI Light", 11))
            amount_entry.place(x=30, y=100)
            amount_entry.insert(0, "Enter amount")
            fullname = current_user.get("full_name")

            def complete_withdraw():
                def get_current_balance():
                    cursor.execute("SELECT account_balance FROM user WHERE account_holder=?", (fullname, ))
                    result = cursor.fetchone()

                    if result:
                        return result[0]

                try:
                    get_amount = float(amount_entry.get())
                    ch.withdraw_balance(self, get_amount, get_current_balance(), fullname)
                    messagebox.showinfo("Success", "Withdraw successfully")
                except:
                    messagebox.showinfo("Success", "Successful")
                    window.destroy()

            tk.Button(window, width=25, text="Withdraw", bg="blue", fg="white", command=complete_withdraw).place(x=27, y=220)

            window.mainloop()

        def check_balance():
            fullname = current_user.get("full_name")
            check = ch.check_balance(self, fullname)
            label1.configure(text=f"Your balance is {check}")
            return check

        def change_lock():
            window = tk.Tk()
            window.title("Change Password")
            window.geometry("300x300+300+200")
            window.resizable(False, False)
            old_password_entry = tk.Entry(width=25, fg="black", border=0, bg="white", font=("Micrfosoft YaHei UI Light", 11))
            new_password_entry = tk.Entry(width=25, fg="black", border=0, bg="white", font=("Micrfosoft YaHei UI Light", 11))
            confirm_password_entry = tk.Entry(width=25, fg="black", border=0, bg="white", font=("Micrfosoft YaHei UI Light", 11))
            old_password_entry.place(x=30, y=100)
            new_password_entry.place(x=30, y=150)
            confirm_password_entry.place(x=30, y=200)
            old_password_entry.insert(0, "Enter old Password")
            new_password_entry.insert(0, "Enter new Password")
            confirm_password_entry.insert(0, "Confirm new Password")
            def change_password():
                fullname = current_user.get("full_name")
                try:
                    cursor.execute("SELECT password FROM user WHERE account_holder=?", (fullname,))
                    result = cursor.fetchone()
                    if result:
                        get_old_password = old_password_entry.get()
                        old_pw_hash = bcrypt.checkpw(get_old_password.encode("utf-8"), result[0])
                        if bcrypt.checkpw(get_old_password.encode("utf-8"), result[0]):
                            # print(old_pw_hash)
                            # print(result[0])
                            if new_password_entry.get() == confirm_password_entry.get():
                                ask = messagebox.askyesno("Change password", "Are you sure you would like to change your password")
                                if ask:
                                    messagebox.showinfo("Success", "Password changed successfully")
                                    ch.update_password(self, fullname, new_password_entry.get())
                                    window.destroy()
                        else:
                            messagebox.showerror("Error", "Old password incorrect")
                except:
                    messagebox.showerror("Error", "Invalid Input")
            
            tk.Button(window, text="Change PIN", command=change_password, bg="#C53F3F", font=("Microsoft YaHei UI Light", 23, "bold")).place(x=30, y=250)
            window.mainloop()


        label = tk.Label(self, text=f"Welcome", border=0, bg="white", fg="#C53F3F", font=("Microsoft YaHei UI Light", 23, "bold"))
        label.place(x=350, y=15)

        label2 = tk.Label(self, text="What would you like to do?", border=0, bg="white",fg="#C53F3F", font=("Microsoft YaHei UI Light", 23, "bold"))
        label2.place(x=260, y=50)

        label1 = tk.Label(self, border=0, bg="white",fg="#C53F3F", font=("Microsoft YaHei UI Light", 23, "bold"))
        label1.place(x=290, y=90)

        btn1 = tk.Button(self, width=30, pady=5, text="Deposit", bg="#C53F3F", fg="white", border=0, command=deposit)
        btn2 = tk.Button(self, width=30, pady=5, text="Withdraw", bg="#C53F3F", fg="white", border=0, command=withdraw)
        btn3 = tk.Button(self, width=30, pady=5, text="Check Balance", bg="#C53F3F", fg="white", border=0, command=check_balance)
        btn4 = tk.Button(self, width=30, pady=5, text="Change pin", bg="#C53F3F", fg="white", border=0, command=change_lock)

        btn1.place(x=80, y=180)
        btn2.place(x=540, y=180)
        btn3.place(x=80, y=230)
        btn4.place(x=540, y=230)


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # creating the window
        window = tk.Frame(self, bg="#fff")
        window.configure(background="#F0F0F0")
        window.pack()

        window.grid_rowconfigure(0, minsize=500)
        window.grid_columnconfigure(0, minsize=925)
        

        self.frames = {}
        for F in (Signin, Signup, Mainpage):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

            if F == Signin:
                self.title("Login")
            elif F == Signup:
                self.title("Signup")

        self.show_frame(Signin)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()


# initializing application
app = Application()
app.geometry("925x500+400+200")
app.resizable(False, False)
app.mainloop()
