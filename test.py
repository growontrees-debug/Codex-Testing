"""Open a window displaying a greeting for Ron."""

import tkinter as tk


def main():
    window = tk.Tk()
    window.title("Hello Ron")
    window.geometry("320x160")
    tk.Label(window, text="Hello Ron.", font=("Arial", 24)).pack(expand=True)
    window.mainloop()


if __name__ == "__main__":
    main()
