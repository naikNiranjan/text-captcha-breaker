"""
Simple CAPTCHA Solver GUI
========================

A standalone GUI application for solving CAPTCHAs using clipboard, file upload, or screen capture.
All dependencies included in one file.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageGrab
import threading
import time
import pyperclip
import pyautogui
import os
import sys

# CAPTCHA Solving Core (from app.py)
import torch
import onnx
import onnxruntime as rt
from torchvision import transforms as T
from tokenizer_base import Tokenizer

class SimpleCaptchaSolver:
    def __init__(self):
        """Initialize the CAPTCHA solver"""
        self.model_file = "captcha.onnx"
        self.img_size = (32, 128)
        self.charset = r"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        
        # Check if model file exists
        if not os.path.exists(self.model_file):
            raise FileNotFoundError(f"Model file '{self.model_file}' not found!")
        
        # Initialize tokenizer and model
        self.tokenizer = Tokenizer(self.charset)
        self.transform, self.ort_session = self._initialize_model()
    
    def _get_transform(self):
        """Get image transform"""
        transforms = [
            T.Resize(self.img_size, T.InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(0.5, 0.5)
        ]
        return T.Compose(transforms)
    
    def _to_numpy(self, tensor):
        """Convert tensor to numpy"""
        return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()
    
    def _initialize_model(self):
        """Initialize ONNX model"""
        transform = self._get_transform()
        
        # Load ONNX model
        onnx_model = onnx.load(self.model_file)
        onnx.checker.check_model(onnx_model)
        ort_session = rt.InferenceSession(self.model_file)
        
        return transform, ort_session
    
    def solve_captcha(self, img):
        """Solve CAPTCHA from PIL Image"""
        try:
            # Preprocess image
            x = self.transform(img.convert('RGB')).unsqueeze(0)
            
            # Run inference
            ort_inputs = {self.ort_session.get_inputs()[0].name: self._to_numpy(x)}
            logits = self.ort_session.run(None, ort_inputs)[0]
            probs = torch.tensor(logits).softmax(-1)
            
            # Decode result
            preds, probs = self.tokenizer.decode(probs)
            result = preds[0]
            
            print(f"CAPTCHA solved: {result}")
            return result
            
        except Exception as e:
            print(f"Error solving CAPTCHA: {e}")
            return None

class SimpleCaptchaGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple CAPTCHA Solver")
        self.root.geometry("700x600")
        
        # Initialize solver
        try:
            self.solver = SimpleCaptchaSolver()
            self.solver_ready = True
        except Exception as e:
            self.solver_ready = False
            messagebox.showerror("Error", f"Failed to initialize CAPTCHA solver:\n{e}")
        
        self.current_image = None
        self.monitoring = False
        self.monitor_thread = None
        
        self.setup_ui()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="9e0 Simple CAPTCHA Solver", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Status indicator
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        status_text = "197 Solver Ready" if self.solver_ready else "6d1 Solver Not Ready"
        status_color = "green" if self.solver_ready else "red"
        ttk.Label(status_frame, text=status_text, foreground=status_color, 
                 font=("Arial", 10, "bold")).pack()
        
        # Methods frame
        methods_frame = ttk.LabelFrame(main_frame, text="Choose Your Method", padding="15")
        methods_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Method 1: Clipboard
        clipboard_frame = ttk.Frame(methods_frame)
        clipboard_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(clipboard_frame, text="4cb Method 1: Clipboard", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(clipboard_frame, text="Right-click CAPTCHA 9 Copy Image 9 Click button below", 
                 foreground="gray").pack(anchor=tk.W, pady=(0, 5))
        
        button_frame1 = ttk.Frame(clipboard_frame)
        button_frame1.pack(fill=tk.X)
        
        self.clipboard_btn = ttk.Button(button_frame1, text="4cb Solve from Clipboard", 
                                       command=self.solve_from_clipboard,
                                       style="Accent.TButton")
        self.clipboard_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.monitor_btn = ttk.Button(button_frame1, text="504 Start Auto-Monitor", 
                                     command=self.toggle_monitoring)
        self.monitor_btn.pack(side=tk.LEFT)
        
        self.monitor_status = tk.StringVar(value="Not monitoring")
        ttk.Label(button_frame1, textvariable=self.monitor_status, 
                 foreground="blue").pack(side=tk.RIGHT)
        
        # Method 2: File Upload
        file_frame = ttk.Frame(methods_frame)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(file_frame, text="4c2 Method 2: File Upload", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(file_frame, text="Save CAPTCHA as image file and load it here", 
                 foreground="gray").pack(anchor=tk.W, pady=(0, 5))
        
        self.file_btn = ttk.Button(file_frame, text="4c2 Load Image File", 
                                  command=self.load_image_file)
        self.file_btn.pack(anchor=tk.W)
        
        # Method 3: Screen Capture
        screen_frame = ttk.Frame(methods_frame)
        screen_frame.pack(fill=tk.X)
        
        ttk.Label(screen_frame, text="4f8 Method 3: Screen Capture", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(screen_frame, text="Select CAPTCHA region on your screen", 
                 foreground="gray").pack(anchor=tk.W, pady=(0, 5))
        
        self.screen_btn = ttk.Button(screen_frame, text="4f8 Capture Screen Region", 
                                    command=self.capture_screen_region)
        self.screen_btn.pack(anchor=tk.W)
        
        # Image display
        image_frame = ttk.LabelFrame(main_frame, text="CAPTCHA Image", padding="15")
        image_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.image_label = ttk.Label(image_frame, text="No CAPTCHA image loaded\nUse one of the methods above")
        self.image_label.pack()
        
        # Solution display
        solution_frame = ttk.LabelFrame(main_frame, text="af Solution", padding="15")
        solution_frame.pack(fill=tk.X, pady=(0, 20))
        
        solution_container = ttk.Frame(solution_frame)
        solution_container.pack(fill=tk.X)
        
        self.solution_var = tk.StringVar(value="No solution yet")
        self.solution_label = ttk.Label(solution_container, textvariable=self.solution_var, 
                                       font=("Arial", 16, "bold"), foreground="blue")
        self.solution_label.pack(side=tk.LEFT)
        
        self.copy_btn = ttk.Button(solution_container, text="4cb Copy Solution", 
                                  command=self.copy_solution, state="disabled")
        self.copy_btn.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Choose a method above")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        # Disable buttons if solver not ready
        if not self.solver_ready:
            self.clipboard_btn.config(state="disabled")
            self.monitor_btn.config(state="disabled")
            self.file_btn.config(state="disabled")
            self.screen_btn.config(state="disabled")
    
    def solve_from_clipboard(self):
        """Solve CAPTCHA from clipboard image"""
        try:
            self.status_var.set("Checking clipboard for image...")
            
            # Get image from clipboard
            img = ImageGrab.grabclipboard()
            
            if img is None:
                messagebox.showwarning("No Image", 
                    "No image found in clipboard!\n\n" +
                    "Steps:\n" +
                    "1. Right-click on CAPTCHA image\n" +
                    "2. Select 'Copy Image'\n" +
                    "3. Click this button again")
                self.status_var.set("No image in clipboard")
                return
            
            # Display image
            self.display_image(img)
            
            # Solve CAPTCHA
            self.status_var.set("Solving CAPTCHA...")
            solution = self.solver.solve_captcha(img)
            
            if solution:
                self.solution_var.set(solution)
                self.copy_btn.config(state="normal")
                self.status_var.set(f"✅ Solved: {solution}")
                
                # Auto-copy to clipboard
                pyperclip.copy(solution)
                messagebox.showinfo("Success!", 
                    f"CAPTCHA Solved: {solution}\n\n" +
                    "✅ Solution copied to clipboard automatically!")
            else:
                self.status_var.set("❌ Could not solve CAPTCHA")
                messagebox.showerror("Error", "Could not solve this CAPTCHA")
                
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Error processing clipboard: {str(e)}")
    
    def toggle_monitoring(self):
        """Start or stop clipboard monitoring"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start monitoring clipboard for CAPTCHA images"""
        self.monitoring = True
        self.monitor_btn.config(text="⏹️ Stop Auto-Monitor")
        self.monitor_status.set("🔄 Monitoring active")
        
        def monitor_loop():
            last_clipboard = None
            while self.monitoring:
                try:
                    current_clipboard = ImageGrab.grabclipboard()
                    
                    if (current_clipboard is not None and 
                        current_clipboard != last_clipboard):
                        
                        # New image detected
                        self.root.after(0, lambda: self.auto_solve_clipboard(current_clipboard))
                        last_clipboard = current_clipboard
                    
                    time.sleep(1)  # Check every second
                    
                except Exception as e:
                    print(f"Monitor error: {e}")
                    time.sleep(2)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.status_var.set("🔄 Auto-monitoring started - copy any CAPTCHA!")
    
    def stop_monitoring(self):
        """Stop clipboard monitoring"""
        self.monitoring = False
        self.monitor_btn.config(text="🔄 Start Auto-Monitor")
        self.monitor_status.set("Not monitoring")
        self.status_var.set("⏹️ Auto-monitoring stopped")
    
    def auto_solve_clipboard(self, img):
        """Automatically solve CAPTCHA from clipboard"""
        try:
            self.display_image(img)
            solution = self.solver.solve_captcha(img)
            
            if solution:
                self.solution_var.set(solution)
                self.copy_btn.config(state="normal")
                pyperclip.copy(solution)
                
                self.status_var.set(f"✅ Auto-solved: {solution}")
                
                # Show notification
                self.root.bell()  # System sound
                messagebox.showinfo("Auto-Solved!", 
                    f"CAPTCHA: {solution}\n\n✅ Solution copied to clipboard!")
            
        except Exception as e:
            self.status_var.set(f"❌ Auto-solve error: {str(e)}")
    
    def load_image_file(self):
        """Load CAPTCHA image from file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select CAPTCHA Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg *.jpeg"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # Load and display image
            img = Image.open(file_path)
            self.display_image(img)
            
            # Solve CAPTCHA
            self.status_var.set("Solving loaded image...")
            solution = self.solver.solve_captcha(img)
            
            if solution:
                self.solution_var.set(solution)
                self.copy_btn.config(state="normal")
                pyperclip.copy(solution)
                self.status_var.set(f"✅ Solved: {solution}")
                messagebox.showinfo("Success!", f"CAPTCHA Solved: {solution}")
            else:
                self.status_var.set("❌ Could not solve image")
                messagebox.showerror("Error", "Could not solve this image")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading image: {str(e)}")
    
    def capture_screen_region(self):
        """Capture a region of the screen"""
        try:
            messagebox.showinfo("Screen Capture", 
                "Instructions:\n\n" +
                "1. Click OK to start\n" +
                "2. This window will minimize\n" +
                "3. Click and drag to select CAPTCHA area\n" +
                "4. Window will restore automatically")
            
            # Minimize window
            self.root.withdraw()
            time.sleep(0.5)
            
            # Get screen coordinates from user
            self.start_screen_selection()
            
        except Exception as e:
            self.root.deiconify()
            messagebox.showerror("Error", f"Screen capture failed: {str(e)}")
    
    def start_screen_selection(self):
        """Start screen region selection"""
        # Take screenshot first
        screenshot = ImageGrab.grab()
        
        # Create selection window
        selection_window = tk.Toplevel()
        selection_window.title("Select CAPTCHA Region")
        selection_window.attributes('-fullscreen', True)
        selection_window.attributes('-alpha', 0.3)
        selection_window.configure(bg='gray')
        
        canvas = tk.Canvas(selection_window, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = tk.Label(selection_window, 
                              text="Click and drag to select CAPTCHA region • Press ESC to cancel",
                              bg='yellow', font=('Arial', 12, 'bold'))
        instructions.place(x=10, y=10)
        
        selection_coords = {}
        
        def start_selection(event):
            selection_coords['start_x'] = event.x
            selection_coords['start_y'] = event.y
            selection_coords['rect'] = canvas.create_rectangle(
                event.x, event.y, event.x, event.y, outline='red', width=3)
        
        def update_selection(event):
            if 'rect' in selection_coords:
                canvas.coords(selection_coords['rect'], 
                            selection_coords['start_x'], selection_coords['start_y'],
                            event.x, event.y)
        
        def end_selection(event):
            if 'rect' in selection_coords:
                x1, y1 = selection_coords['start_x'], selection_coords['start_y']
                x2, y2 = event.x, event.y
                
                # Ensure x1,y1 is top-left
                if x1 > x2:
                    x1, x2 = x2, x1
                if y1 > y2:
                    y1, y2 = y2, y1
                
                # Close selection window
                selection_window.destroy()
                
                # Restore main window
                self.root.deiconify()
                
                # Crop screenshot
                if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:  # Minimum size check
                    cropped = screenshot.crop((x1, y1, x2, y2))
                    
                    # Display and solve
                    self.display_image(cropped)
                    self.status_var.set("Solving selected region...")
                    
                    solution = self.solver.solve_captcha(cropped)
                    if solution:
                        self.solution_var.set(solution)
                        self.copy_btn.config(state="normal")
                        pyperclip.copy(solution)
                        self.status_var.set(f"✅ Solved: {solution}")
                        messagebox.showinfo("Success!", f"CAPTCHA Solved: {solution}")
                    else:
                        self.status_var.set("❌ Could not solve selected region")
                        messagebox.showerror("Error", "Could not solve selected region")
                else:
                    self.status_var.set("Selection too small")
        
        def cancel_selection(event):
            selection_window.destroy()
            self.root.deiconify()
            self.status_var.set("Selection cancelled")
        
        # Bind events
        canvas.bind('<Button-1>', start_selection)
        canvas.bind('<B1-Motion>', update_selection)
        canvas.bind('<ButtonRelease-1>', end_selection)
        canvas.bind('<Escape>', cancel_selection)
        selection_window.bind('<Escape>', cancel_selection)
        
        canvas.focus_set()
    
    def display_image(self, img):
        """Display image in the GUI"""
        try:
            # Resize image for display
            display_size = (400, 120)
            img_display = img.copy()
            img_display.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img_display)
            
            # Update label
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep reference
            
            self.current_image = img
            
        except Exception as e:
            print(f"Display error: {e}")
    
    def copy_solution(self):
        """Copy solution to clipboard"""
        solution = self.solution_var.get()
        if solution and solution != "No solution yet":
            pyperclip.copy(solution)
            messagebox.showinfo("Copied!", f"Solution '{solution}' copied to clipboard!")
    
    def on_closing(self):
        """Handle window closing"""
        try:
            self.stop_monitoring()
        except:
            pass
        finally:
            self.root.destroy()
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

def main():
    """Main function"""
    try:
        # Check if required files exist
        required_files = ["captcha.onnx", "tokenizer_base.py"]
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            print("Please ensure these files are in the same directory as this script.")
            input("Press Enter to exit...")
            return
        
        print("🚀 Starting Simple CAPTCHA Solver GUI...")
        app = SimpleCaptchaGUI()
        app.run()
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
