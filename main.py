import face_recognition
import cv2
import os
import numpy as np
import csv
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Load images and get face encodings for multiple people
known_face_encodings = []
known_face_names = []

# Add Soham's image
soham_image_path = "/Users/sam/Desktop/sam/images/your_image.jpg"  # Adjust the path
soham_image = face_recognition.load_image_file(soham_image_path)
soham_face_encoding = face_recognition.face_encodings(soham_image)[0]
known_face_encodings.append(soham_face_encoding)
known_face_names.append("Soham")

# Add a second person's image (e.g., John)
john_image_path = "/Users/sam/Desktop/sam/images/shubham.jpg"  # Adjust the path
john_image = face_recognition.load_image_file(john_image_path)
john_face_encoding = face_recognition.face_encodings(john_image)[0]
known_face_encodings.append(john_face_encoding)
known_face_names.append("shubham")

# Open the attendance CSV file to log attendance
attendance_file = 'attendance.csv'

# Function to log attendance
def log_attendance(name, manual=False, time=None):
    with open(attendance_file, 'a', newline='') as file:
        writer = csv.writer(file)
        current_time = time if manual else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([name, current_time])
        messagebox.showinfo("Attendance Logged", f"{name} present at {current_time}")

# Function to handle camera attendance
def camera_attendance():
    # Initialize the video capture
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        messagebox.showerror("Error", "Unable to open the webcam.")
        return

    # Track which faces have been marked as present
    attendance_marked = set()

    while True:
        # Capture a single frame of video
        ret, frame = video_capture.read()

        if not ret:
            messagebox.showerror("Error", "Failed to capture video frame.")
            break

        # Find all face locations and face encodings in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Loop through each face found in the frame
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Check if the face matches with any known face
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            # If the person is detected and not already marked, log attendance
            if name not in attendance_marked:
                log_attendance(name)
                attendance_marked.add(name)  # Mark the person as present to avoid multiple entries

            # Draw a rectangle around the face and label it
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close all OpenCV windows
    video_capture.release()
    cv2.destroyAllWindows()

# Function for manual attendance
def manual_attendance():
    name = entry_name.get()
    time = entry_time.get()
    if not name:
        messagebox.showerror("Error", "Please enter a student name.")
        return
    log_attendance(name, manual=True, time=time if time else None)

# Create the GUI window
root = tk.Tk()
root.title("Attendance System")

# Label and buttons
label = tk.Label(root, text="Choose an option to mark attendance:")
label.pack(pady=10)

camera_button = tk.Button(root, text="Open Camera", command=camera_attendance)
camera_button.pack(pady=5)

manual_frame = tk.Frame(root)
manual_frame.pack(pady=10)

entry_name_label = tk.Label(manual_frame, text="Student Name:")
entry_name_label.grid(row=0, column=0)
entry_name = tk.Entry(manual_frame)
entry_name.grid(row=0, column=1)

entry_time_label = tk.Label(manual_frame, text="Time (YYYY-MM-DD HH:MM:SS):")
entry_time_label.grid(row=1, column=0)
entry_time = tk.Entry(manual_frame)
entry_time.grid(row=1, column=1)

manual_button = tk.Button(root, text="Mark Manually", command=manual_attendance)
manual_button.pack(pady=5)

exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=5)

# Run the GUI loop
root.mainloop()
