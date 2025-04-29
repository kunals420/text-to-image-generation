import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import io
import requests
from PIL import Image, ImageTk


class EasyImageGeneratorApp:
    def __init__(self, root):
        # Set up the API key (hardcoded for simplicity)
        self.API_KEY = "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"
        # Use a public model with fewer restrictions
        self.API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"


        self.root = root
        self.root.title("Easy Image Generator")
        self.root.geometry("550x500")

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create input area
        input_frame = ttk.LabelFrame(main_frame, text="What image do you want?", padding="10")
        input_frame.pack(fill=tk.X, pady=10)

        # Text input
        self.prompt_text = scrolledtext.ScrolledText(input_frame, height=3, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.X, expand=True)
        self.prompt_text.insert(tk.END, "A cat wearing a space suit")
++                                                                                                                                                                                                                                                                                            222 3


        # Style selector
        style_frame = ttk.Frame(input_frame)
        style_frame.pack(fill=tk.X, pady=5)

        ttk.Label(style_frame, text="Style:").pack(side=tk.LEFT, padx=5)
        self.style_var = tk.StringVar(value="digital art")
        styles = ["digital art", "oil painting", "pixel art", "watercolor", "photorealistic",
                  "anime", "sketch", "cyberpunk", "3D render", "none"]
        style_menu = ttk.Combobox(style_frame, textvariable=self.style_var, values=styles)
        style_menu.pack(side=tk.LEFT, padx=5)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # Generate button with improved styling
        button_style = ttk.Style()
        button_style.configure("Generate.TButton", font=("Arial", 11, "bold"))

        self.generate_button = ttk.Button(
            button_frame,
            text="Generate Image",
            command=self.generate_image,
            style="Generate.TButton"
        )
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # Save button
        self.save_button = ttk.Button(
            button_frame,
            text="Save Image",
            command=self.save_image,
            state=tk.DISABLED
        )
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_var = tk.StringVar(value="Ready to generate images!")
        self.status_label = ttk.Label(button_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT, padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)

        # Image display area
        self.image_frame = ttk.LabelFrame(main_frame, text="Generated Image", padding="10")
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Store the generated image
        self.generated_image = None

    def generate_image(self):
        # Get the prompt
        prompt = self.prompt_text.get("1.0", tk.END).strip()

        # Check if we have what we need
        if not prompt:
            messagebox.showinfo("Missing Info", "Please enter what image you want to create")
            return

        # Add style to prompt if selected
        style = self.style_var.get()
        if style and style != "none":
            full_prompt = f"{prompt}, {style}"
        else:
            full_prompt = prompt

        # Disable UI during generation
        self.generate_button.configure(state=tk.DISABLED)
        self.status_var.set("Creating your image...")
        self.progress.start()

        # Start generation in a separate thread
        thread = threading.Thread(target=self._generate_image_thread, args=(full_prompt,))
        thread.daemon = True
        thread.start()

    def _generate_image_thread(self, prompt):
        try:
            # Set up the API request
            headers = {"Authorization": f"Bearer {self.API_KEY}"}

            # Make the API call
            response = requests.post(
                self.API_URL,
                headers=headers,
                json={"inputs": prompt}
            )

            # Handle different responses
            if response.status_code == 200:
                # Success! Process the image
                image_bytes = response.content
                image = Image.open(io.BytesIO(image_bytes))
                self.generated_image = image
                self.root.after(0, self._generation_complete)

            elif response.status_code == 503:
                # Model is loading
                self.root.after(0, lambda: self.status_var.set("The AI model is warming up, please wait..."))

                # Wait a bit and try again (5 seconds)
                self.root.after(5000, lambda: self._generate_image_thread(prompt))

            elif response.status_code == 401:
                # Invalid API key
                error_msg = "Invalid API key. The included API key may have expired."
                self.root.after(0, lambda: self._generation_error(error_msg))

            elif response.status_code == 403:
                # Forbidden - likely due to model permissions
                error_msg = "Access forbidden. This API key doesn't have permission to use this model.\n\nTry using a different model or accept the model terms on Hugging Face website."
                self.root.after(0, lambda: self._generation_error(error_msg))

            else:
                # Other error
                try:
                    error_detail = response.json().get('error', 'Unknown error')
                    error_msg = f"Error ({response.status_code}): {error_detail}"
                except:
                    error_msg = f"Error: The server returned status code {response.status_code}"
                self.root.after(0, lambda: self._generation_error(error_msg))

        except Exception as e:
            self.root.after(0, lambda: self._generation_error(str(e)))

    def _generation_complete(self):
        self.progress.stop()
        self.status_var.set("Image created successfully!")
        self.generate_button.configure(state=tk.NORMAL)
        self.save_button.configure(state=tk.NORMAL)

        # Resize image for display
        display_img = self.generated_image.copy()
        display_img.thumbnail((400, 400))

        # Convert PIL image to Tkinter PhotoImage
        photo = ImageTk.PhotoImage(display_img)

        # Update image display
        self.image_label.configure(image=photo)
        self.image_label.image = photo  # Keep a reference

    def _generation_error(self, error_msg):
        self.progress.stop()
        self.status_var.set(f"Error: {error_msg}")
        self.generate_button.configure(state=tk.NORMAL)
        messagebox.showerror("Error", f"Could not create image: {error_msg}")

    def save_image(self):
        if self.generated_image is None:
            return

        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.generated_image.save(file_path)
                self.status_var.set(f"Image saved!")
                messagebox.showinfo("Success", "Your image was saved successfully!")
            except Exception as e:
                self.status_var.set(f"Error saving image")
                messagebox.showerror("Save Error", f"Could not save image: {str(e)}")


def show_error_solution():
    """Show a specific message about 403 errors and how to fix them"""
    messagebox.showinfo(
        "Important: Fixing 403 Errors",
        "If you get a 403 Forbidden error, it means you need to accept the model terms on Hugging Face:\n\n"
        "1. Go to huggingface.co and log in\n"
        "2. Search for 'stable-diffusion-2-1'\n"
        "3. Visit the model page\n"
        "4. Click 'Agree' on the model terms\n\n"
        "After doing this, the app should work correctly!"
    )


def main():
    root = tk.Tk()
    app = EasyImageGeneratorApp(root)

    # Show instructions first
    messagebox.showinfo(
        "Welcome to Easy Image Generator",
        "Simply type what image you want to create, choose a style, and click 'Generate Image'!"
    )

    # Then show specific info about fixing 403 errors
    root.after(1000, show_error_solution)

    root.mainloop()


if __name__ == "__main__":
    main()