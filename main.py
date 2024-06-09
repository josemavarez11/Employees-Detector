import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import pandas as pd
import qrcode
import numpy as np
import os
from PIL import Image

csv_file = 'employees.csv'

def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

def register_employee():
    name = entry_name.get()
    if name:
        df = pd.DataFrame([[name]], columns=['Name'])
        if os.path.isfile(csv_file):
            df.to_csv(csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_file, index=False)

        qr_image = generate_qr(name)
        qr_image_file = f'{name}.png'
        qr_image.save(qr_image_file)
        
        img = Image.open(qr_image_file)
        img.show()
        
        messagebox.showinfo("Register", "user registered successfully")
    else:
        messagebox.showwarning("Invalid input", "Please, enter a name to register")

def validate_employee():
    if not os.path.isfile(csv_file):
        messagebox.showwarning("Error", "There are not employees registered in the system")
        return

    try:
        employees_df = pd.read_csv(csv_file)
        if 'Name' not in employees_df.columns:
            raise KeyError("Row 'Name' doesn't exists in CSV file")
    except Exception as e:
        messagebox.showerror("Error", f"Error reading CSV file: {e}")
        return

    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        data, bbox, _ = detector.detectAndDecode(frame)

        if bbox is not None:
            bbox = np.int32(bbox).reshape(-1, 2) 
            color = (0, 0, 255)
            text = "Unauthorized"

            if data:
                if data in employees_df['Name'].values:
                    color = (0, 255, 0)
                    text = f"Employee {data} authorized"
                else:
                    text = f"Unauthorized"

            for i in range(len(bbox)):
                cv2.line(frame, tuple(bbox[i]), tuple(bbox[(i+1) % len(bbox)]), color, 3)

            cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

        cv2.imshow('Employee Validation', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

root = tk.Tk()
root.title("Register and Validation for Employees")
root.geometry("500x400") 

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True, fill="both")

label_instrucciones = ttk.Label(frame, text="Enter your name to register", font=("Helvetica", 12))
label_instrucciones.pack(pady=10)

entry_name = ttk.Entry(frame, font=("Helvetica", 12))
entry_name.pack(pady=5)

btn_registrar = ttk.Button(frame, text="Register", command=register_employee)
btn_registrar.pack(pady=5)

btn_validar = ttk.Button(frame, text="Validate", command=validate_employee)
btn_validar.pack(pady=5)

root.mainloop()
