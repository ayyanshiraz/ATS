import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ats_logic import ATSScanner
import threading
from PIL import Image
import requests
from io import BytesIO

# Configuration for the UI appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Window Setup - Increased height slightly to fit the new "Submitted To" section
        self.geometry("600x720") 
        self.overrideredirect(True)  # Removes the window title bar and borders
        self.attributes('-topmost', True)  # Keeps the splash screen on top
        
        # Center the splash screen on the monitor
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 720) // 2
        self.geometry(f"600x720+{x}+{y}")
        self.configure(fg_color="#1a1a1a") # Dark background

        # 1. Logo Display (FROM URL - Fixed)
        # We use the direct link to the image
        image_url = "https://i.ibb.co/XkLVwNCG/logo.png"
        
        try:
            response = requests.get(image_url)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            # Resize image to be nice and visible
            logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
            ctk.CTkLabel(self, image=logo_img, text="").pack(pady=(30, 10))
        except Exception as e:
            print(f"Error loading logo from URL: {e}")
            ctk.CTkLabel(self, text="FAST NUCES", font=("Arial", 20, "bold")).pack(pady=(30, 10))

        # 2. Main Project Title
        ctk.CTkLabel(self, text="Python Project", font=("Roboto", 32, "bold"), text_color="white").pack(pady=5)

        # 3. Subtitle (Course Info)
        course_text = "Final project of Programming For Business Application\nCS4089 MSBA 1A"
        ctk.CTkLabel(self, text=course_text, font=("Roboto", 16), text_color="#AAAAAA").pack(pady=5)

        # 4. Group Participants Title
        ctk.CTkLabel(self, text="Group Participants:", font=("Roboto", 18, "bold"), text_color="#FFaa00").pack(pady=(20, 5))
        
        participants = [
            "Ayyan Shiraz 25L-7309",
            "Malik Sanwal Akhtar 25L-7369",
            "Uzair Arbab 25L-7345",
            "Hafiz Daniyal Khan 25L-7360"
        ]
        
        for p in participants:
            ctk.CTkLabel(self, text=p, font=("Roboto", 14), text_color="white").pack(pady=2)

        # 5. Submitted To (Center Block - NEW)
        ctk.CTkLabel(self, text="Submitted To:", font=("Roboto", 16, "bold"), text_color="#FFaa00").pack(pady=(20, 2))
        ctk.CTkLabel(self, text="Sir Bilal Qaiser", font=("Roboto", 18, "bold"), text_color="white").pack(pady=2)

        # Loading Bar
        self.progress = ctk.CTkProgressBar(self, width=400, height=4, mode="indeterminate", progress_color="#FFaa00")
        self.progress.pack(side="bottom", pady=(0, 60)) # Padded to sit above footer
        self.progress.start()

        # --- SPLASH SCREEN FOOTER ---
        self.footer = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color="#222222")
        self.footer.pack(side="bottom", fill="x")
        
        # Left: License
        group_names = "Licensed to: Ayyan, Sanwal, Uzair, Daniyal"
        ctk.CTkLabel(self.footer, text=group_names, font=("Arial", 10), text_color="#888888").pack(side="left", padx=15, pady=5)

        # Right: Submitted To
        ctk.CTkLabel(self.footer, text="Submitted to: Sir Bilal Qaiser", font=("Arial", 12, "bold"), text_color="#FFaa00").pack(side="right", padx=15, pady=5)


class ATSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Hide the main window immediately
        self.withdraw()
        
        # 2. Show the Splash Screen
        self.splash = SplashScreen(self)
        
        # 3. Schedule the main app to launch after 6 seconds (gave slightly more time to read names)
        self.after(6000, self.launch_main_app)

    def launch_main_app(self):
        """Destroys splash and builds the main application"""
        self.splash.destroy()
        self.setup_main_ui()
        self.deiconify() # Show the main window
        
        # Center the main window
        w, h = 950, 750
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = int((ws/2) - (w/2))
        y = int((hs/2) - (h/2))
        self.geometry(f'{w}x{h}+{x}+{y}')

    def setup_main_ui(self):
        """Builds the actual ATS Scanner Interface"""
        self.title("Python Project - ATS Scanner")
        self.geometry("950x750")
        self.scanner = ATSScanner()
        self.selected_files = []

        # Layout: Grid Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) # Footer row

        # --- Left Sidebar (Inputs) ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(9, weight=1)

        # Sidebar Title
        self.logo_label = ctk.CTkLabel(self.sidebar, text="ATS Scanner", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Buttons
        self.files_btn = ctk.CTkButton(self.sidebar, text="Select Files", command=self.select_files)
        self.files_btn.grid(row=1, column=0, padx=20, pady=10)

        self.folder_btn = ctk.CTkButton(self.sidebar, text="Select Folder", fg_color="orange", hover_color="darkorange", command=self.select_folder)
        self.folder_btn.grid(row=2, column=0, padx=20, pady=10)

        self.file_count_label = ctk.CTkLabel(self.sidebar, text="No files loaded", text_color="gray")
        self.file_count_label.grid(row=3, column=0, padx=20, pady=(0, 10))

        # Settings
        self.sep_label = ctk.CTkLabel(self.sidebar, text="--- Settings ---", text_color="gray")
        self.sep_label.grid(row=4, column=0, padx=20, pady=(10, 5))

        self.n_label = ctk.CTkLabel(self.sidebar, text="Show Top N Candidates:")
        self.n_label.grid(row=5, column=0, padx=20, pady=(5, 0))
        
        self.n_entry = ctk.CTkEntry(self.sidebar, placeholder_text="e.g. 3")
        self.n_entry.insert(0, "5")
        self.n_entry.grid(row=6, column=0, padx=20, pady=5)

        self.strict_label = ctk.CTkLabel(self.sidebar, text="Minimum Match %: 15%")
        self.strict_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        
        self.strict_slider = ctk.CTkSlider(self.sidebar, from_=0, to=100, number_of_steps=20, command=self.update_slider_label)
        self.strict_slider.set(15) 
        self.strict_slider.grid(row=8, column=0, padx=20, pady=5)

        self.process_btn = ctk.CTkButton(self.sidebar, text="Find Best Matches", fg_color="green", hover_color="darkgreen", command=self.start_processing)
        self.process_btn.grid(row=9, column=0, padx=20, pady=20)

        # --- Right Main Area ---
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.jd_label = ctk.CTkLabel(self.main_area, text="Paste Job Description:", font=ctk.CTkFont(size=16))
        self.jd_label.pack(anchor="w")
        
        self.jd_box = ctk.CTkTextbox(self.main_area, height=150)
        self.jd_box.pack(fill="x", pady=(5, 20))

        self.progress = ctk.CTkProgressBar(self.main_area)
        self.progress.set(0)
        self.progress.pack(fill="x", pady=(0, 20))

        self.results_label = ctk.CTkLabel(self.main_area, text="Ranked Results:", font=ctk.CTkFont(size=16))
        self.results_label.pack(anchor="w")

        self.results_frame = ctk.CTkScrollableFrame(self.main_area, height=350)
        self.results_frame.pack(fill="both", expand=True)

        # --- MAIN APP FOOTER ---
        self.footer = ctk.CTkFrame(self, height=35, corner_radius=0, fg_color="#222222")
        self.footer.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        group_names = "Licensed to: Ayyan Shiraz, Malik Sanwal Akhtar, Uzair Arbab, Hafiz Daniyal Khan"
        self.footer_left = ctk.CTkLabel(self.footer, text=group_names, font=("Arial", 11), text_color="#888888")
        self.footer_left.pack(side="left", padx=20, pady=5)

        self.footer_right = ctk.CTkLabel(self.footer, text="Submitted to: Sir Bilal Qaiser", font=("Arial", 12, "bold"), text_color="#FFaa00")
        self.footer_right.pack(side="right", padx=20, pady=5)

    def update_slider_label(self, value):
        self.strict_label.configure(text=f"Minimum Match %: {int(value)}%")

    def select_files(self):
        filetypes = (('PDF files', '*.pdf'), ('Word files', '*.docx'))
        files = filedialog.askopenfilenames(title='Open files', initialdir='/', filetypes=filetypes)
        if files:
            self.selected_files = list(files)
            self.file_count_label.configure(text=f"{len(files)} resumes selected")

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select Resume Folder")
        if folder_path:
            found_files = []
            for root, dirs, filenames in os.walk(folder_path):
                for filename in filenames:
                    if filename.lower().endswith(('.pdf', '.docx')):
                        found_files.append(os.path.join(root, filename))
            
            self.selected_files = found_files
            self.file_count_label.configure(text=f"{len(found_files)} resumes selected")

    def start_processing(self):
        jd_text = self.jd_box.get("1.0", "end-1c")
        
        if not self.selected_files:
            messagebox.showwarning("Error", "Please load resumes first.")
            return
        if len(jd_text) < 10:
            messagebox.showwarning("Error", "Please enter a valid Job Description.")
            return

        self.process_btn.configure(state="disabled", text="Processing...")
        self.progress.set(0)
        threading.Thread(target=self.run_analysis, args=(jd_text,), daemon=True).start()

    def run_analysis(self, jd_text):
        self.scanner.load_resumes(self.selected_files, progress_callback=self.update_progress)
        try:
            top_n = int(self.n_entry.get())
        except ValueError:
            top_n = 3
            
        threshold = self.strict_slider.get()
        results = self.scanner.get_top_candidates(jd_text, top_n, threshold)
        self.display_results(results)
        self.process_btn.configure(state="normal", text="Find Best Matches")

    def update_progress(self, value):
        self.progress.set(value)

    def display_results(self, df):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if df.empty:
            lbl = ctk.CTkLabel(
                self.results_frame, 
                text="❌ No suitable candidates found.\n\nTry lowering the 'Minimum Match %' slider\nor check a different Job Description.",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            lbl.pack(pady=50)
            return

        for index, row in df.iterrows():
            card = ctk.CTkFrame(self.results_frame, fg_color="#2B2B2B")
            card.pack(fill="x", pady=5, padx=5)

            name_lbl = ctk.CTkLabel(card, text=f"#{index+1}: {row['Candidate']}", font=ctk.CTkFont(size=14, weight="bold"))
            name_lbl.pack(side="left", padx=10, pady=10)

            score = row['Match %']
            if score > 70:
                score_color = "#00FF00"
            elif score > 40:
                score_color = "orange"
            else:
                score_color = "#FF5555"

            score_lbl = ctk.CTkLabel(card, text=f"{score}% Match", text_color=score_color, font=ctk.CTkFont(weight="bold"))
            score_lbl.pack(side="right", padx=10, pady=10)

if __name__ == "__main__":
    app = ATSApp()
    app.mainloop()