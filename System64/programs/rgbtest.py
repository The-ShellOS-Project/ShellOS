import tkinter as tk

root = tk.Tk()
root.title("RGBTEST")
root.geometry("300x300")  

canvas = tk.Canvas(root, width=300, height=300)
canvas.pack()

height = 300
width = 300
quadrant_height = height // 3

canvas.create_rectangle(0, 0, width, quadrant_height, fill="red", outline="")
canvas.create_rectangle(0, quadrant_height, width, 2 * quadrant_height, fill="green", outline="")
canvas.create_rectangle(0, 2 * quadrant_height, width, height, fill="blue", outline="")
root.mainloop()
