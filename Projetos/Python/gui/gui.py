import tkinter as tk
from tkinter import messagebox

def greet():
    nome = entry.get()
    if nome:
        messagebox.showinfo("Comprimentando", f"Olá, {nome}!")
    else:
        messagebox.showwarning("Input Error", "Please enter your name.")

root = tk.Tk()
root.title("Janela Titulo")
root.geometry("300x150")

label = tk.Label(root, text="Escreva aki porra")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=5)

button = tk.Button(root, text="Dizer ola", command=greet)
button.pack(pady=10)

root.mainloop()