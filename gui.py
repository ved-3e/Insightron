import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import os
import logging
from typing import Optional
from config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModernButton(tk.Canvas):
    """Custom modern button with hover effects"""
    def __init__(self, parent, text, command, bg_color, fg_color, hover_color, **kwargs):
        self.height = kwargs.pop('height', 45)
        self.width = kwargs.pop('width', 200)
        super().__init__(parent, height=self.height, width=self.width, 
                        bg=parent['bg'], highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.text = text
        self.is_hovered = False
        self.enabled = True
        
        self.draw_button()
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
    def draw_button(self):
        self.delete('all')
        color = self.hover_color if self.is_hovered and self.enabled else self.bg_color
        
        # Rounded rectangle
        radius = 8
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, radius, 
                                fill=color, outline='')
        
        # Text
        self.create_text(self.width/2, self.height/2, text=self.text, 
                        fill=self.fg_color, font=('Segoe UI', 11, 'bold'))
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, e):
        if self.enabled:
            self.is_hovered = True
            self.draw_button()
            self.config(cursor='hand2')
    
    def on_leave(self, e):
        self.is_hovered = False
        self.draw_button()
        self.config(cursor='')
    
    def on_click(self, e):
        if self.enabled and self.command:
            self.command()
    
    def set_state(self, state):
        self.enabled = (state == 'normal')
        self.draw_button()


class InsightronGUI:
    """
    Enhanced GUI for Insightron - A modern interface for audio transcription
    """
    
    def __init__(self, root: tk.Tk):
        """Initialize the Insightron GUI"""
        self.root = root
        self.root.title("Insightron")
        self.root.geometry("900x750")
        
        # Modern color palette - Dark elegant theme
        self.colors = {
            'bg_primary': '#0A0E27',      # Deep dark blue
            'bg_secondary': '#131829',     # Slightly lighter
            'bg_card': '#1A1F3A',          # Card background
            'accent': '#6366F1',           # Indigo accent
            'accent_hover': '#818CF8',     # Lighter indigo
            'accent_dim': '#4F46E5',       # Darker indigo
            'text_primary': '#F8FAFC',     # Almost white
            'text_secondary': '#94A3B8',   # Muted blue-gray
            'text_dim': '#64748B',         # Dimmer text
            'success': '#10B981',          # Green
            'border': '#1E293B',           # Subtle border
            'shadow': '#000000',           # Shadow
        }
        
        # Configure window
        self.root.configure(bg=self.colors['bg_primary'])
        self.root.resizable(True, True)
        self.root.minsize(700, 600)
        
        # State
        self.selected_file = None
        self.is_transcribing = False
        self.transcriber = None
        self.animation_id = None
        
        # Setup custom styles
        self.setup_styles()
        
        # Setup UI
        self.setup_ui()
        self.center_window()
        
        # Start subtle background animation
        self.animate_background()
        
        logger.info("GUI initialized successfully")
        
    def setup_styles(self):
        """Setup custom ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Combobox style
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['bg_card'],
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='flat')
        
        # Progressbar style
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['bg_secondary'],
                       borderwidth=0,
                       thickness=6)
        
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
    
    def create_glow_effect(self, canvas, x, y, radius, color):
        """Create a glowing circle effect"""
        for i in range(3, 0, -1):
            alpha = int(20 / i)
            r = radius + (i * 15)
            # Simulate alpha by using darker shades
            canvas.create_oval(x-r, y-r, x+r, y+r, 
                             fill='', outline=color, width=2)
    
    def setup_ui(self):
        """Setup the main UI"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Content wrapper with padding
        content = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # ===== ANIMATED HEADER =====
        header_frame = tk.Frame(content, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 35))
        
        # Logo canvas with pulse effect
        self.logo_canvas = tk.Canvas(header_frame, width=60, height=60,
                                     bg=self.colors['bg_primary'],
                                     highlightthickness=0)
        self.logo_canvas.pack(side=tk.LEFT, padx=(0, 15))
        
        # Draw logo - stylized waveform
        self.draw_logo()
        
        # Title section
        title_section = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        title_section.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title = tk.Label(title_section, text="Insightron", 
                        bg=self.colors['bg_primary'],
                        fg=self.colors['text_primary'],
                        font=('Segoe UI', 32, 'bold'))
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_section, 
                           text="Local AI Transcription  •  Private  •  Precise  •  Powered by Whisper",
                           bg=self.colors['bg_primary'],
                           fg=self.colors['text_secondary'],
                           font=('Segoe UI', 10))
        subtitle.pack(anchor=tk.W, pady=(2, 0))
        
        # Decorative line
        line_canvas = tk.Canvas(content, height=2, bg=self.colors['bg_primary'],
                               highlightthickness=0)
        line_canvas.pack(fill=tk.X, pady=(0, 30))
        line_canvas.create_rectangle(0, 0, 900, 2, 
                                     fill=self.colors['border'], outline='')
        
        # ===== FILE UPLOAD CARD =====
        file_card = self.create_card(content, "")
        file_card.pack(fill=tk.X, pady=(0, 20))
        
        # Drop zone style area
        drop_zone = tk.Frame(file_card, bg=self.colors['bg_secondary'],
                            highlightthickness=1,
                            highlightbackground=self.colors['border'])
        drop_zone.pack(fill=tk.X, padx=2, pady=2)
        
        drop_inner = tk.Frame(drop_zone, bg=self.colors['bg_secondary'])
        drop_inner.pack(fill=tk.X, padx=25, pady=25)
        
        # File icon and text
        icon_label = tk.Label(drop_inner, text="🎵",
                            bg=self.colors['bg_secondary'],
                            fg=self.colors['accent'],
                            font=('Segoe UI', 32))
        icon_label.pack(pady=(0, 12))
        
        self.file_path_var = tk.StringVar(value="No audio file selected")
        file_label = tk.Label(drop_inner, textvariable=self.file_path_var,
                             bg=self.colors['bg_secondary'], 
                             fg=self.colors['text_secondary'],
                             font=('Segoe UI', 11))
        file_label.pack(pady=(0, 15))
        
        # Browse button
        browse_frame = tk.Frame(drop_inner, bg=self.colors['bg_secondary'])
        browse_frame.pack()
        
        self.browse_btn = ModernButton(browse_frame, "Choose Audio File", 
                                       self.browse_file,
                                       self.colors['accent'],
                                       self.colors['text_primary'],
                                       self.colors['accent_hover'],
                                       width=180, height=42)
        self.browse_btn.pack()
        
        # Supported formats
        formats = tk.Label(drop_inner, 
                          text="MP3  •  WAV  •  M4A  •  FLAC  •  MP4  •  OGG",
                          bg=self.colors['bg_secondary'],
                          fg=self.colors['text_dim'],
                          font=('Segoe UI', 9))
        formats.pack(pady=(12, 0))
        
        # ===== SETTINGS GRID =====
        settings_card = self.create_card(content, "Configuration")
        settings_card.pack(fill=tk.X, pady=(0, 20))
        
        settings_grid = tk.Frame(settings_card, bg=self.colors['bg_card'])
        settings_grid.pack(fill=tk.X, padx=25, pady=20)
        
        # Model selection
        model_col = tk.Frame(settings_grid, bg=self.colors['bg_card'])
        model_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        tk.Label(model_col, text="WHISPER MODEL",
                bg=self.colors['bg_card'],
                fg=self.colors['text_dim'],
                font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(model_col, textvariable=self.model_var,
                                   values=["tiny", "base", "small", "medium", "large"],
                                   state="readonly", 
                                   style='Modern.TCombobox',
                                   font=('Segoe UI', 10))
        model_combo.pack(fill=tk.X)
        
        tk.Label(model_col, text="Balance speed & accuracy",
                bg=self.colors['bg_card'],
                fg=self.colors['text_dim'],
                font=('Segoe UI', 8)).pack(anchor=tk.W, pady=(5, 0))
        
        # Language selection
        language_col = tk.Frame(settings_grid, bg=self.colors['bg_card'])
        language_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        tk.Label(language_col, text="LANGUAGE",
                bg=self.colors['bg_card'],
                fg=self.colors['text_dim'],
                font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        
        self.language_var = tk.StringVar(value=DEFAULT_LANGUAGE)
        # Create language options list with display names
        language_options = []
        for code, name in SUPPORTED_LANGUAGES.items():
            if code == 'auto':
                language_options.append(f"{code} - {name}")
            else:
                language_options.append(f"{code} - {name}")
        
        language_combo = ttk.Combobox(language_col, textvariable=self.language_var,
                                      values=language_options,
                                      state="readonly",
                                      style='Modern.TCombobox',
                                      font=('Segoe UI', 10))
        language_combo.pack(fill=tk.X)
        
        tk.Label(language_col,
                text="Auto-detect or specify language",
                bg=self.colors['bg_card'],
                fg=self.colors['text_dim'],
                font=('Segoe UI', 8)).pack(anchor=tk.W, pady=(5, 0))
        
        # Formatting selection
        format_col = tk.Frame(settings_grid, bg=self.colors['bg_card'])
        format_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(format_col, text="TEXT FORMATTING",
                bg=self.colors['bg_card'],
                fg=self.colors['text_dim'],
                font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        
        self.formatting_var = tk.StringVar(value="auto")
        format_combo = ttk.Combobox(format_col, textvariable=self.formatting_var,
                                    values=["auto", "paragraphs", "minimal"],
                                    state="readonly",
                                    style='Modern.TCombobox',
                                    font=('Segoe UI', 10))
        format_combo.pack(fill=tk.X)
        
        tk.Label(format_col,
                text="Smart paragraph detection",
                bg=self.colors['bg_card'],
                fg=self.colors['text_dim'],
                font=('Segoe UI', 8)).pack(anchor=tk.W, pady=(5, 0))
        
        # ===== PROGRESS CARD =====
        progress_card = self.create_card(content, "Status")
        progress_card.pack(fill=tk.X, pady=(0, 20))
        
        progress_inner = tk.Frame(progress_card, bg=self.colors['bg_card'])
        progress_inner.pack(fill=tk.X, padx=25, pady=20)
        
        self.progress_var = tk.StringVar(value="Ready to transcribe")
        progress_label = tk.Label(progress_inner, textvariable=self.progress_var,
                                 bg=self.colors['bg_card'],
                                 fg=self.colors['text_secondary'],
                                 font=('Segoe UI', 11))
        progress_label.pack(anchor=tk.W, pady=(0, 12))
        
        self.progress_bar = ttk.Progressbar(progress_inner, 
                                           mode='indeterminate',
                                           style='Modern.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X)
        
        # ===== ACTION BUTTON =====
        action_frame = tk.Frame(content, bg=self.colors['bg_primary'])
        action_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.transcribe_btn = ModernButton(action_frame, 
                                          "⚡ Start Transcription",
                                          self.start_transcription,
                                          self.colors['accent'],
                                          self.colors['text_primary'],
                                          self.colors['accent_hover'],
                                          width=240, height=50)
        self.transcribe_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        self.clear_btn = ModernButton(action_frame, "Clear",
                                     self.clear_all,
                                     self.colors['bg_card'],
                                     self.colors['text_secondary'],
                                     self.colors['bg_secondary'],
                                     width=100, height=50)
        self.clear_btn.pack(side=tk.LEFT)
        
        # ===== RESULTS CARD =====
        results_card = self.create_card(content, "Transcription Output")
        results_card.pack(fill=tk.BOTH, expand=True)
        
        results_inner = tk.Frame(results_card, bg=self.colors['bg_card'])
        results_inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Text widget with custom styling
        text_frame = tk.Frame(results_inner, 
                             bg=self.colors['bg_secondary'],
                             highlightthickness=1,
                             highlightbackground=self.colors['border'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, bg=self.colors['bg_card'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(text_frame, wrap=tk.WORD,
                                   font=('Consolas', 10),
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['text_secondary'],
                                   insertbackground=self.colors['accent'],
                                   yscrollcommand=scrollbar.set,
                                   relief=tk.FLAT,
                                   padx=15, pady=15,
                                   spacing1=2, spacing3=2)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)
        
        self.results_text.config(state='disabled')
    
    def draw_logo(self):
        """Draw animated logo"""
        self.logo_canvas.delete('all')
        
        # Gradient circle background
        center = 30
        for i in range(28, 0, -2):
            alpha = int(255 * (i / 28))
            color_value = 99 + int((139 - 99) * (1 - i / 28))
            color = f'#{color_value:02x}66F1'
            self.logo_canvas.create_oval(center-i, center-i, center+i, center+i,
                                        fill=color, outline='')
        
        # Waveform bars
        bars = [12, 18, 24, 18, 12]
        x_start = 15
        for i, height in enumerate(bars):
            x = x_start + (i * 8)
            y_top = center - height // 2
            y_bottom = center + height // 2
            self.logo_canvas.create_rectangle(x, y_top, x+4, y_bottom,
                                            fill='#F8FAFC', outline='')
    
    def animate_background(self):
        """Subtle pulsing animation for logo"""
        # This creates a breathing effect
        if hasattr(self, 'logo_canvas'):
            self.draw_logo()
            self.animation_id = self.root.after(2000, self.animate_background)
    
    def create_card(self, parent, title):
        """Create a modern card container"""
        card = tk.Frame(parent, bg=self.colors['bg_card'],
                       highlightthickness=1,
                       highlightbackground=self.colors['border'])
        
        if title:
            header = tk.Frame(card, bg=self.colors['bg_card'])
            header.pack(fill=tk.X, padx=25, pady=(18, 0))
            
            tk.Label(header, text=title,
                    bg=self.colors['bg_card'],
                    fg=self.colors['text_primary'],
                    font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W)
        
        return card
    
    def browse_file(self):
        """Open file dialog"""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.m4a *.flac *.mp4 *.ogg *.aac"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=filetypes
        )
        
        if filename:
            self.selected_file = filename
            file_name = Path(filename).name
            # Truncate if too long
            if len(file_name) > 50:
                file_name = file_name[:47] + "..."
            self.file_path_var.set(f"✓ {file_name}")
            self.update_results(f"✓ Selected: {file_name}\n")
            logger.info(f"File selected: {filename}")
    
    def start_transcription(self):
        """Start transcription"""
        if not self.selected_file:
            messagebox.showerror("No File", "Please select an audio file first.")
            return
        
        if self.is_transcribing:
            messagebox.showwarning("In Progress", "Transcription already in progress.")
            return
        
        # Disable buttons
        self.transcribe_btn.set_state('disabled')
        self.browse_btn.set_state('disabled')
        self.is_transcribing = True
        
        # Start progress bar
        self.progress_bar.start(8)
        self.progress_var.set("⚙️ Initializing Whisper AI...")
        
        # Clear results
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')
        
        # Start transcription in thread
        thread = threading.Thread(target=self.transcribe_audio, daemon=True)
        thread.start()
    
    def transcribe_audio(self):
        """Perform transcription"""
        try:
            # Import here to avoid loading at startup
            from transcribe import AudioTranscriber
            from config import TRANSCRIPTION_FOLDER
            
            # Initialize
            self.update_progress("🔄 Loading Whisper model...")
            self.transcriber = AudioTranscriber(self.model_var.get())
            
            # Transcribe
            def progress_callback(msg):
                self.update_progress(f"🎙️ {msg}")
            
            # Extract language code from selection
            selected_language = self.language_var.get()
            if ' - ' in selected_language:
                language_code = selected_language.split(' - ')[0]
            else:
                language_code = selected_language
            
            self.update_progress("🎙️ Transcribing audio...")
            output_path, data = self.transcriber.transcribe_file(
                self.selected_file,
                progress_callback=progress_callback,
                formatting_style=self.formatting_var.get(),
                language=language_code
            )
            
            # Success
            self.update_progress("✓ Transcription completed successfully!")
            
            result = f"""╔══════════════════════════════════════════════════════════════╗
║  ✓ TRANSCRIPTION COMPLETE                                    ║
╚══════════════════════════════════════════════════════════════╝

📁 Output: {output_path.name}

📊 Transcription Details:
   • Duration: {data.get('duration', 'N/A')}
   • Model: {data.get('model', self.model_var.get())}
   • Language: {data.get('language', 'N/A')}
   • Characters: {len(data.get('text', '')):,}

💾 Saved to: {TRANSCRIPTION_FOLDER}

Ready for your next transcription!
"""
            
            self.update_results(result)
            
            # Ask to open folder
            self.root.after(0, lambda: self.show_success_dialog(output_path))
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            self.update_progress("✗ Transcription failed")
            self.update_results(f"\n✗ ERROR: {str(e)}\n")
            messagebox.showerror("Error", f"Transcription failed:\n{str(e)}")
        
        finally:
            self.root.after(0, self.reset_ui)
    
    def show_success_dialog(self, output_path):
        """Show success dialog"""
        if messagebox.askyesno("Success!", 
                              "Transcription completed successfully!\n\nOpen output folder?"):
            try:
                os.startfile(str(output_path.parent))
            except:
                # For non-Windows systems
                import subprocess
                try:
                    subprocess.run(['xdg-open', str(output_path.parent)])
                except:
                    subprocess.run(['open', str(output_path.parent)])
    
    def update_progress(self, message):
        """Thread-safe progress update"""
        self.root.after(0, lambda: self.progress_var.set(message))
    
    def update_results(self, message):
        """Thread-safe results update"""
        def append():
            self.results_text.config(state='normal')
            self.results_text.insert(tk.END, message)
            self.results_text.see(tk.END)
            self.results_text.config(state='disabled')
        
        self.root.after(0, append)
    
    def reset_ui(self):
        """Reset UI after transcription"""
        self.progress_bar.stop()
        self.transcribe_btn.set_state('normal')
        self.browse_btn.set_state('normal')
        self.is_transcribing = False
    
    def clear_all(self):
        """Clear all fields"""
        self.file_path_var.set("No audio file selected")
        self.selected_file = None
        
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')
        
        self.progress_var.set("Ready to transcribe")
        self.progress_bar.stop()
        
        logger.info("UI cleared")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = InsightronGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()