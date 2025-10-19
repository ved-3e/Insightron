#!/usr/bin/env python3
"""
Test script to demonstrate the new macOS-style GUI
"""

import tkinter as tk
from gui import WhisperTranscriberGUI

def main():
    """Test the macOS-style GUI"""
    print("Testing macOS-style Whisper AI Transcriber GUI...")
    
    root = tk.Tk()
    app = WhisperTranscriberGUI(root)
    
    # Add some test content to show the interface
    app.update_results("Welcome to the macOS-style Whisper AI Transcriber!")
    app.update_results("This interface features:")
    app.update_results("• Clean, card-based layout")
    app.update_results("• macOS color palette and typography")
    app.update_results("• Smooth animations and hover effects")
    app.update_results("• Professional spacing and alignment")
    app.update_results("• Glass morphism-inspired design")
    
    print("GUI launched successfully!")
    print("Features:")
    print("- macOS-style color scheme")
    print("- Card-based layout")
    print("- Smooth animations")
    print("- Professional typography")
    print("- Hover effects")
    
    root.mainloop()

if __name__ == "__main__":
    main()
