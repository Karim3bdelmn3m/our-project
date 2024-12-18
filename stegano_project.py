# -*- coding: utf-8 -*-
"""
Created on Sat Dec 14 14:15:54 2024

@author: Kareem
"""
from stegano import lsb
from os.path import isfile, join
import time
import math
import os
import shutil
from subprocess import call, STDOUT
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import wave
import numpy as np
import cv2

class SteganographyTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography Tool")
        self.root.geometry("600x500")
        
        self.main_menu()

    def main_menu(self):
        self.clear_window()
        tk.Label(self.root, text="Steganography Tool", font=("Helvetica", 16, "bold")).pack(pady=20)
        tk.Label(self.root, text="Choose a Category", font=("Helvetica", 12)).pack(pady=10)

        tk.Button(self.root, text="Audio", font=("Helvetica", 12), width=20, command=lambda: self.tool_page("Audio")).pack(pady=5)
        tk.Button(self.root, text="Video", font=("Helvetica", 12), width=20, command=lambda: self.tool_page("Video")).pack(pady=5)
        tk.Button(self.root, text="Text", font=("Helvetica", 12), width=20, command=lambda: self.tool_page("Text")).pack(pady=5)
        tk.Button(self.root, text="Image", font=("Helvetica", 12), width=20, command=lambda: self.tool_page("Image")).pack(pady=5)

    def tool_page(self, category):
        self.clear_window()
        tk.Label(self.root, text=f"{category} Steganography", font=("Helvetica", 16, "bold")).pack(pady=20)

        tk.Button(self.root, text="Encode", font=("Helvetica", 12), width=20, command=lambda: self.encode_page(category)).pack(pady=10)
        tk.Button(self.root, text="Decode", font=("Helvetica", 12), width=20, command=lambda: self.decode_page(category)).pack(pady=10)

        tk.Button(self.root, text="Back", font=("Helvetica", 12), command=self.main_menu).pack(pady=20)

    def encode_page(self, category):
        self.clear_window()
        tk.Label(self.root, text=f"{category} Encoding", font=("Helvetica", 16, "bold")).pack(pady=10)

        tk.Label(self.root, text="Enter Data to Hide:").pack(pady=5)
        hidden_message_entry = tk.Entry(self.root, width=40)
        hidden_message_entry.pack(pady=5)

        tk.Label(self.root, text="Select File Path for Encoding:").pack(pady=5)
        file_path_entry = tk.Entry(self.root, width=40)
        file_path_entry.pack(pady=5)
        tk.Button(self.root, text="Browse", command=lambda: self.browse_file(file_path_entry)).pack(pady=5)

        tk.Label(self.root, text="Enter New File Name and Extension:").pack(pady=5)
        new_file_entry = tk.Entry(self.root, width=40)
        new_file_entry.pack(pady=5)

        tk.Button(self.root, text="Encode", font=("Helvetica", 12), command=lambda: self.encode_action(hidden_message_entry.get(), file_path_entry.get(), new_file_entry.get(), category)).pack(pady=10)

        self.back_exit_buttons()

    def decode_page(self, category):
        self.clear_window()
        tk.Label(self.root, text=f"{category} Decoding", font=("Helvetica", 16, "bold")).pack(pady=10)

        tk.Label(self.root, text="Choose File to Decode:").pack(pady=5)
        file_path_entry = tk.Entry(self.root, width=40)
        file_path_entry.pack(pady=5)
        tk.Button(self.root, text="Browse", command=lambda: self.browse_file(file_path_entry)).pack(pady=5)

        tk.Button(self.root, text="Decode", font=("Helvetica", 12), command=lambda: self.decode_action(file_path_entry.get(), category)).pack(pady=10)

        self.back_exit_buttons()

    def browse_file(self, entry):
        file_path = filedialog.askopenfilename()
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

    def encode_action(self, hidden_message, file_path, new_file_name, category):
        if not hidden_message or not file_path or not new_file_name:
            messagebox.showerror("Error", "All fields are required!")
            return

        if category == "Image":
            self.encode_image(hidden_message, file_path, new_file_name)
        elif category == "Audio":
            self.encode_audio(hidden_message, file_path, new_file_name)
        elif category == "Text":
            self.encode_text(hidden_message, file_path, new_file_name)
        elif category == "Video":
            self.encode_video(hidden_message, file_path, new_file_name)
        
        messagebox.showinfo("Success", f"Data encoded successfully in {new_file_name}!")

    def decode_action(self, file_path, category):
        if not file_path:
            messagebox.showerror("Error", "File path is required!")
            return

        decoded_message = ""

        if category == "Image":
            decoded_message = self.decode_image(file_path)
        elif category == "Audio":
            decoded_message = self.decode_audio(file_path)
        elif category == "Text":
            decoded_message = self.decode_text(file_path)
        elif category == "Video":
            decoded_message = self.decode_video(file_path)
        
        messagebox.showinfo("Decoded Message", decoded_message)

    def encode_image(self, hidden_message, image_path, new_file_name):
        img = Image.open(image_path)
        binary_message = ''.join(format(ord(char), '08b') for char in hidden_message)
        binary_message += '1111111111111110'  # End of message delimiter
        pixels = img.load()

        message_index = 0
        for i in range(img.width):
            for j in range(img.height):
                pixel = list(pixels[i, j])
                for k in range(3):  # Loop through RGB channels
                    if message_index < len(binary_message):
                        pixel[k] = pixel[k] & 0xFE | int(binary_message[message_index])
                        message_index += 1
                pixels[i, j] = tuple(pixel)

        img.save(new_file_name)

    def decode_image(self, image_path):
        img = Image.open(image_path)
        pixels = img.load()
        
        binary_message = ""
        for i in range(img.width):
            for j in range(img.height):
                pixel = pixels[i, j]
                for k in range(3):  # Loop through RGB channels
                    binary_message += str(pixel[k] & 1)

        byte_message = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
        decoded_message = "".join(chr(int(byte, 2)) for byte in byte_message if int(byte, 2) != 255)
        return decoded_message

    def encode_audio(self, hidden_message, audio_path, new_file_name):
        audio = wave.open(audio_path, 'rb')
        frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
        
        binary_message = ''.join(format(ord(char), '08b') for char in hidden_message)
        binary_message += '1111111111111110'  # End of message delimiter
        message_index = 0

        for i in range(len(frame_bytes)):
            if message_index < len(binary_message):
                frame_bytes[i] = frame_bytes[i] & 0xFE | int(binary_message[message_index])
                message_index += 1

        with wave.open(new_file_name, 'wb') as encoded_audio:
            encoded_audio.setparams(audio.getparams())
            encoded_audio.writeframes(bytes(frame_bytes))

    def decode_audio(self, audio_path):
        audio = wave.open(audio_path, 'rb')
        frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
        
        binary_message = ""
        for byte in frame_bytes:
            binary_message += format(byte, '08b')[-1]

        byte_message = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
        decoded_message = "".join(chr(int(byte, 2)) for byte in byte_message if int(byte, 2) != 255)
        return decoded_message

    def encode_text(self, hidden_message, text_path, new_file_name):
        # Using Caesar Cipher for text encoding
        shift = 3
        encoded_message = ''.join(chr((ord(c) + shift) % 256) for c in hidden_message)

        with open(new_file_name, 'w') as file:
            file.write(encoded_message)

    def decode_text(self, text_path):
        with open(text_path, 'r') as file:
            encoded_message = file.read()
        
        shift = 3
        decoded_message = ''.join(chr((ord(c) - shift) % 256) for c in encoded_message)
        return decoded_message

    def encode_video(self, hidden_message, video_path, new_file_name):
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()

        binary_message = ''.join(format(ord(char), '08b') for char in hidden_message)
        binary_message += '1111111111111110'  # End of message delimiter
        message_index = 0

        while ret:
            for i in range(frame.shape[0]):
                for j in range(frame.shape[1]):
                    if message_index < len(binary_message):
                        pixel = frame[i, j]
                        frame[i, j] = pixel & 0xFE | int(binary_message[message_index])
                        message_index += 1
            ret, frame = cap.read()

        cap.release()
        cv2.imwrite(new_file_name, frame)

    def decode_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        binary_message = ""

        while ret:
            for i in range(frame.shape[0]):
                for j in range(frame.shape[1]):
                    binary_message += str(frame[i, j] & 1)

            ret, frame = cap.read()

        byte_message = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
        decoded_message = "".join(chr(int(byte, 2)) for byte in byte_message if int(byte, 2) != 255)
        cap.release()
        return decoded_message

    def back_exit_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Back", font=("Helvetica", 12), command=self.main_menu).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Exit", font=("Helvetica", 12), command=self.root.quit).pack(side=tk.LEFT, padx=10)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyTool(root)
    root.mainloop()