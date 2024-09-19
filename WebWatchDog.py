import tkinter as tk
from tkinter import messagebox, scrolledtext
import webbrowser
import subprocess
import re
import threading
import time

class SplashScreen(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title("Welcome")
        self.geometry("400x300")
        self.configure(bg="black")

        # Center the content using a Frame with pack options
        self.center_frame = tk.Frame(self, bg="white")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Label for splash screen message
        self.label1 = tk.Label(self, text="Web WatchDog", font=("Times New Roman", 20, "bold"), bg="black", fg="white")
        self.label1.pack(pady=(30, 10))  # Add some padding to position it nicely

        self.label2 = tk.Label(self, text="Your trusty web scanner", font=("Times New Roman", 16), bg="black", fg="white")
        self.label2.pack()

        # Automatically close splash screen after a delay
        self.after(5000, self.destroy)  # 7 seconds delay before closing splash screen

class WapitiGUI:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide the main window initially

        # Show the splash screen
        self.splash = SplashScreen(root)
        self.root.after(5000, self.show_main_window)  # Delay to show main window

    def show_main_window(self):
        self.splash.destroy()  # Close the splash screen
        self.root.deiconify()  # Show the main window
        self.root.title("Web WatchDog")
        self.root.geometry("800x600")

        # Label for the web address input
        self.url_label = tk.Label(self.root, text="Enter Web Address:", font=("Times New Roman", 16))
        self.url_label.pack(pady=10)

        # Entry box for the web address
        self.url_entry = tk.Entry(self.root, width=50, font=("Times New Roman", 14))
        self.url_entry.pack(pady=5)

        # Button to start the Wapiti scan
        self.scan_button = tk.Button(self.root, text="Scan Web Address", command=self.run_wapiti_scan)
        self.scan_button.pack(pady=10)

        # ScrolledText widget to show the Wapiti output
        self.output_text = scrolledtext.ScrolledText(self.root, width=70, height=15, font=("Times New Roman", 12))
        self.output_text.pack(pady=10)

        # Button to open the report
        self.open_report_button = tk.Button(self.root, text="Open Report", command=self.open_report, state=tk.DISABLED)
        self.open_report_button.pack(pady=5)

        # Button to exit the application
        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack(pady=10)

        self.report_path = None  # Variable to store the report path

    def run_wapiti_scan(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid web address.")
            return

        # Disable the scan button during the scan
        self.scan_button.config(state=tk.DISABLED)
        self.open_report_button.config(state=tk.DISABLED)  # Disable the report button

        # Clear previous output
        self.output_text.delete(1.0, tk.END)

        # Start a thread to run the Wapiti scan
        threading.Thread(target=self.scan_thread, args=(url,), daemon=True).start()

    def scan_thread(self, url):
        # Construct the command
        command = ["wapiti", "-u", url, "--flush-session", "-f", "html"]

        try:
            # Run Wapiti command
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Read and display output in real-time
            for line in process.stdout:
                self.update_output(line)
            
            # Collect any remaining output
            stderr = process.stderr.read()
            self.update_output(stderr)

            # Wait for process to complete
            process.wait()

            # Check for the report path in the output
            full_output = self.output_text.get(1.0, tk.END)
            report_path_match = re.search(r'Open (.+\.html) with a browser to see this report', full_output)
            if report_path_match:
                self.report_path = report_path_match.group(1).strip()
                # Enable the report button
                self.root.after(0, lambda: self.open_report_button.config(state=tk.NORMAL))
                # Inform user of success
                self.show_message("Success", "Wapiti scan completed. You can now open the report.")
            else:
                self.show_message("Error", "Report file was not found in Wapiti output.")

        except subprocess.CalledProcessError as e:
            self.show_message("Error", f"Wapiti scan failed: {e.stderr}")

        finally:
            # Re-enable the scan button after the scan is complete
            self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL))

    def update_output(self, text):
        # Update the ScrolledText widget with new output in a thread-safe manner
        self.root.after(0, lambda: self.output_text.insert(tk.END, text))
        self.root.after(0, lambda: self.output_text.see(tk.END))

    def open_report(self):
        if self.report_path:
            # Open the report directly in the web browser
            webbrowser.open_new_tab(f"file://{self.report_path}")

    def show_message(self, title, message):
        # Show a message box in a thread-safe manner
        self.root.after(0, lambda: messagebox.showinfo(title, message))

if __name__ == "__main__":
    root = tk.Tk()
    app = WapitiGUI(root)
    root.mainloop()
