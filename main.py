import customtkinter as ctk
from PIL import Image
import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import CTkMessagebox

# --- Standalone Closing Handler ---
def handle_app_closing(app_instance):
    """
    Standalone function to handle the window closing event.
    This prevents context loss of 'self' in the callback.
    """
    if app_instance.is_closing:
        return # Prevent re-entry
    app_instance.is_closing = True

    if app_instance.is_logged_in:
        app_instance.is_logged_in = False
        if app_instance.main_app_frame and app_instance.main_app_frame.winfo_exists():
            app_instance.main_app_frame.destroy()
        app_instance.main_app_frame = None
        app_instance.is_closing = False # Reset flag for next time
        app_instance.show_login_frame()
    else:
        app_instance.quit()

# --- Constants ---
DATA_FILE = "passwords.json.enc"
MASTER_PASSWORD_SALT_FILE = "salt.bin"

class App(ctk.CTk):
    """
    Clase principal de la aplicación Gestor de Contraseñas.
    """
    def __init__(self):
        super().__init__()
        self.title("Gestor de Contraseñas")
        self.geometry("800x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.master_password = None
        self.fernet = None
        self.passwords = {}
        self.is_logged_in = False
        self.is_closing = False
        self.main_app_frame = None
        self.login_frame = None

        self.protocol("WM_DELETE_WINDOW", lambda: handle_app_closing(self))
        self.show_login_frame()

    def show_login_frame(self):
        self.login_frame = LoginFrame(master=self, on_login_success=self.on_login_success)
        self.login_frame.grid(row=0, column=0, sticky="nsew")

    def on_login_success(self, master_password: str):
        self.is_logged_in = True
        self.master_password = master_password
        self.fernet = self.derive_fernet_key(master_password)
        self.load_passwords()
        if self.login_frame and self.login_frame.winfo_exists():
            self.login_frame.destroy()
        self.login_frame = None
        self.show_main_app_frame()

    def show_main_app_frame(self):
        self.main_app_frame = MainAppFrame(master=self)
        self.main_app_frame.grid(row=0, column=0, sticky="nsew")

    def get_salt(self) -> bytes:
        if os.path.exists(MASTER_PASSWORD_SALT_FILE):
            with open(MASTER_PASSWORD_SALT_FILE, "rb") as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(MASTER_PASSWORD_SALT_FILE, "wb") as f:
                f.write(salt)
        return salt

    def derive_fernet_key(self, master_password: str) -> Fernet:
        salt = self.get_salt()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return Fernet(key)

    def load_passwords(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "rb") as f:
                    encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data).decode()
                self.passwords = json.loads(decrypted_data)
            except Exception as e:
                print(f"Error loading or decrypting data: {e}")
                self.passwords = {}
        else:
            self.passwords = {}

    def save_passwords(self):
        try:
            json_data = json.dumps(self.passwords, indent=4)
            encrypted_data = self.fernet.encrypt(json_data.encode())
            with open(DATA_FILE, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Error saving or encrypting data: {e}")

class LoginFrame(ctk.CTkFrame):
    """
    Frame para la pantalla de inicio de sesión de la aplicación.
    """
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.label = ctk.CTkLabel(self, text="Ingrese Contraseña Maestra", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, pady=20)
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Contraseña Maestra", show="*", width=200)
        self.password_entry.grid(row=1, column=0, pady=10)
        self.password_entry.bind("<Return>", self.login_event)
        self.login_button = ctk.CTkButton(self, text="Iniciar Sesión", command=self.login_event)
        self.login_button.grid(row=2, column=0, pady=10)
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=3, column=0)

    def login_event(self, event=None):
        master_password = self.password_entry.get()
        if not master_password:
            self.error_label.configure(text="La contraseña no puede estar vacía.")
            return
        if not os.path.exists(DATA_FILE) and not os.path.exists(MASTER_PASSWORD_SALT_FILE):
            try:
                self.master.on_login_success(master_password)
                self.master.save_passwords()
            except Exception as e:
                self.error_label.configure(text=f"Error al establecer contraseña: {e}")
            return
        try:
            fernet_test = self.master.derive_fernet_key(master_password)
            with open(DATA_FILE, "rb") as f:
                encrypted_data = f.read()
            fernet_test.decrypt(encrypted_data)
            self.on_login_success(master_password)
        except Exception:
            self.error_label.configure(text="Contraseña maestra incorrecta.")

class MainAppFrame(ctk.CTkFrame):
    """
    Frame principal de la aplicación que muestra la lista de contraseñas.
    """
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.current_selected_entry = None

        # Load Icons
        icon_size = (24, 24)
        self.nav_icon = ctk.CTkImage(Image.open("icons/Navigation.png"), size=icon_size)
        self.add_icon = ctk.CTkImage(Image.open("icons/Add.png"), size=icon_size)
        self.password_icon = ctk.CTkImage(Image.open("icons/Password.png"), size=icon_size)
        self.edit_icon = ctk.CTkImage(Image.open("icons/Edit.png"), size=icon_size)
        self.delete_icon = ctk.CTkImage(Image.open("icons/Delete.png"), size=icon_size)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=80, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="", image=self.nav_icon)
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        button_width = 40
        self.add_button = ctk.CTkButton(self.sidebar_frame, text="", image=self.add_icon, width=button_width, command=self.add_new_entry)
        self.add_button.grid(row=1, column=0, padx=20, pady=10)

        self.generate_button = ctk.CTkButton(self.sidebar_frame, text="", image=self.password_icon, width=button_width, command=self.show_password_generator)
        self.generate_button.grid(row=2, column=0, padx=20, pady=10)

        self.edit_button = ctk.CTkButton(self.sidebar_frame, text="", image=self.edit_icon, width=button_width, command=self.edit_selected_entry, state="disabled")
        self.edit_button.grid(row=3, column=0, padx=20, pady=10)

        self.delete_button = ctk.CTkButton(self.sidebar_frame, text="", image=self.delete_icon, width=button_width, command=self.delete_selected_entry, state="disabled")
        self.delete_button.grid(row=4, column=0, padx=20, pady=10)

        # Main Content
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Buscar servicio...")
        self.search_entry.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="new")
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_password_list())

        self.password_list_frame = ctk.CTkScrollableFrame(self, label_text="Tus Contraseñas")
        self.password_list_frame.grid(row=0, column=1, padx=(20, 0), pady=(60, 20), sticky="nsew")
        self.password_list_frame.grid_columnconfigure(0, weight=1)

        self.detail_frame = ctk.CTkFrame(self)
        self.detail_frame.grid(row=0, column=2, padx=(0, 20), pady=(20, 20), sticky="nsew")
        self.detail_frame.grid_columnconfigure(0, weight=1)
        self.detail_frame.grid_rowconfigure(5, weight=1)
        self.detail_label = ctk.CTkLabel(self.detail_frame, text="Selecciona una entrada o añade una nueva", font=ctk.CTkFont(size=16))
        self.detail_label.grid(row=0, column=0, padx=20, pady=20)
        self.refresh_password_list()

    def refresh_password_list(self):
        for widget in self.password_list_frame.winfo_children():
            widget.destroy()
        search_query = self.search_entry.get().lower()
        filtered_services = [s for s in self.master.passwords.keys() if search_query in s.lower()]
        sorted_services = sorted(filtered_services)
        for i, service in enumerate(sorted_services):
            button = ctk.CTkButton(self.password_list_frame, text=service, command=lambda s=service: self.show_entry_details(s))
            button.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
        self.edit_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        self.current_selected_entry = None

    def show_entry_details(self, service_name: str):
        self.current_selected_entry = service_name
        self.edit_button.configure(state="normal")
        self.delete_button.configure(state="normal")
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        entry_data = self.master.passwords.get(service_name, {})
        ctk.CTkLabel(self.detail_frame, text=f"Servicio: {service_name}", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        username_label = ctk.CTkLabel(self.detail_frame, text=f"Usuario: {entry_data.get('username', '')}", font=ctk.CTkFont(size=14))
        username_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        copy_username_button = ctk.CTkButton(self.detail_frame, text="Copiar", width=70, command=lambda: self._copy_to_clipboard(entry_data.get('username', '')))
        copy_username_button.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        password_label = ctk.CTkLabel(self.detail_frame, text=f"Contraseña: {entry_data.get('password', '')}", font=ctk.CTkFont(size=14))
        password_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        copy_password_button = ctk.CTkButton(self.detail_frame, text="Copiar", width=70, command=lambda: self._copy_to_clipboard(entry_data.get('password', '')))
        copy_password_button.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.detail_frame, text=f"Notas: {entry_data.get('notes', '')}", font=ctk.CTkFont(size=14)).grid(row=3, column=0, padx=20, pady=5, sticky="w")

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        CTkMessagebox.CTkMessagebox(title="Copiado", message="Texto copiado al portapapeles.", icon="info")

    def add_new_entry(self):
        AddEditEntryDialog(self, self._on_add_save)

    def _on_add_save(self, new_data: dict):
        service = new_data.pop("service")
        if service in self.master.passwords:
            CTkMessagebox.CTkMessagebox(title="Error", message=f"El servicio '{service}' ya existe.", icon="warning")
            return
        self.master.passwords[service] = new_data
        self.master.save_passwords()
        self.refresh_password_list()

    def edit_selected_entry(self):
        if self.current_selected_entry:
            entry_data = self.master.passwords.get(self.current_selected_entry, {})
            dialog_data = entry_data.copy()
            dialog_data["service"] = self.current_selected_entry
            AddEditEntryDialog(self, self._on_edit_save, entry_data=dialog_data)
        else:
            CTkMessagebox.CTkMessagebox(title="Advertencia", message="Selecciona una entrada para editar.", icon="warning")

    def _on_edit_save(self, updated_data: dict):
        service = updated_data.pop("service")
        self.master.passwords[service] = updated_data
        self.master.save_passwords()
        self.refresh_password_list()
        self.show_entry_details(service)

    def delete_selected_entry(self):
        if self.current_selected_entry:
            msg = CTkMessagebox.CTkMessagebox(title="Confirmar Eliminación", message=f"¿Estás seguro de que quieres eliminar '{self.current_selected_entry}'?", icon="question", option_1="No", option_2="Sí")
            response = msg.get()
            if response == "Sí":
                del self.master.passwords[self.current_selected_entry]
                self.master.save_passwords()
                self.refresh_password_list()
                for widget in self.detail_frame.winfo_children():
                    widget.destroy()
                self.detail_label = ctk.CTkLabel(self.detail_frame, text="Selecciona una entrada o añade una nueva", font=ctk.CTkFont(size=16))
                self.detail_label.grid(row=0, column=0, padx=20, pady=20)
            else:
                print("Eliminación cancelada.")

    def show_password_generator(self):
        PasswordGeneratorDialog(self)

class AddEditEntryDialog(ctk.CTkToplevel):
    """
    Diálogo para añadir o editar entradas de contraseñas.
    """
    def __init__(self, master, on_save_callback, entry_data=None):
        super().__init__(master)
        self.on_save_callback = on_save_callback
        self.entry_data = entry_data
        self.title("Añadir/Editar Entrada" if entry_data is None else f"Editar {entry_data.get('service', '')}")
        self.geometry("400x400")
        self.transient(master)
        self.grab_set()
        self.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Servicio:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.service_entry = ctk.CTkEntry(self)
        self.service_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(self, text="Usuario:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(self, text="Contraseña:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.show_password_button = ctk.CTkButton(self, text="Mostrar", width=70, command=self.toggle_password_visibility)
        self.show_password_button.grid(row=2, column=2, padx=5, pady=10)
        # Notes
        ctk.CTkLabel(self, text="Notas:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.notes_textbox = ctk.CTkTextbox(self, height=80)
        self.notes_textbox.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Save and Cancel Buttons
        self.save_button = ctk.CTkButton(self, text="Guardar", command=self.save_entry)
        self.save_button.grid(row=5, column=0, columnspan=3, padx=10, pady=20, sticky="ew")

        self.cancel_button = ctk.CTkButton(self, text="Cancelar", command=self.destroy)
        self.cancel_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        if self.entry_data:
            self.service_entry.insert(0, self.entry_data.get('service', ''))
            self.service_entry.configure(state="disabled")
            self.username_entry.insert(0, self.entry_data.get('username', ''))
            self.password_entry.insert(0, self.entry_data.get('password', ''))
            self.notes_textbox.insert("0.0", self.entry_data.get('notes', ''))

    def toggle_password_visibility(self):
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.show_password_button.configure(text="Ocultar")
        else:
            self.password_entry.configure(show="*")
            self.show_password_button.configure(text="Mostrar")

    def save_entry(self):
        service = self.service_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        notes = self.notes_textbox.get("0.0", "end-1c")
        if not service or not username or not password:
            CTkMessagebox.CTkMessagebox(title="Error", message="Servicio, Usuario y Contraseña no pueden estar vacíos.", icon="warning")
            return
        new_data = {"service": service, "username": username, "password": password, "notes": notes}
        self.on_save_callback(new_data)
        self.destroy()

class PasswordGeneratorDialog(ctk.CTkToplevel):
    """
    Diálogo para generar contraseñas seguras.
    """
    def __init__(self, master):
        super().__init__(master)
        self.title("Generar Contraseña Segura")
        self.geometry("450x400")
        self.transient(master)
        self.grab_set()
        self.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Longitud de la Contraseña:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.length_slider = ctk.CTkSlider(self, from_=8, to=32, number_of_steps=24, command=self.update_length_label)
        self.length_slider.set(16)
        self.length_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.length_label = ctk.CTkLabel(self, text=f"{int(self.length_slider.get())}")
        self.length_label.grid(row=0, column=2, padx=5, pady=10)
        ctk.CTkLabel(self, text="Incluir:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.uppercase_var = ctk.BooleanVar(value=True)
        self.lowercase_var = ctk.BooleanVar(value=True)
        self.digits_var = ctk.BooleanVar(value=True)
        self.symbols_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="Mayúsculas (A-Z)", variable=self.uppercase_var).grid(row=1, column=1, sticky="w", padx=10)
        ctk.CTkCheckBox(self, text="Minúsculas (a-z)", variable=self.lowercase_var).grid(row=2, column=1, sticky="w", padx=10)
        ctk.CTkCheckBox(self, text="Dígitos (0-9)", variable=self.digits_var).grid(row=3, column=1, sticky="w", padx=10)
        ctk.CTkCheckBox(self, text="Símbolos (!@#$)", variable=self.symbols_var).grid(row=4, column=1, sticky="w", padx=10)
        ctk.CTkLabel(self, text="Contraseña Generada:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.generated_password_entry = ctk.CTkEntry(self, state="readonly")
        self.generated_password_entry.grid(row=5, column=1, padx=10, pady=10, sticky="ew")
        self.generate_button = ctk.CTkButton(self, text="Generar", command=self.generate_password)
        self.generate_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.copy_button = ctk.CTkButton(self, text="Copiar al Portapapeles", command=self.copy_to_clipboard)
        self.copy_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.close_button = ctk.CTkButton(self, text="Cerrar", command=self.destroy)
        self.close_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.generate_password()

    def update_length_label(self, value: float):
        self.length_label.configure(text=f"{int(value)}")

    def generate_password(self):
        import secrets
        import string
        length = int(self.length_slider.get())
        characters = ""
        if self.uppercase_var.get(): characters += string.ascii_uppercase
        if self.lowercase_var.get(): characters += string.ascii_lowercase
        if self.digits_var.get(): characters += string.digits
        if self.symbols_var.get(): characters += string.punctuation
        if not characters:
            self.generated_password_entry.configure(state="normal")
            self.generated_password_entry.delete(0, ctk.END)
            self.generated_password_entry.insert(0, "Selecciona al menos un tipo de carácter")
            self.generated_password_entry.configure(state="readonly")
            return
        password = ''.join(secrets.choice(characters) for i in range(length))
        self.generated_password_entry.configure(state="normal")
        self.generated_password_entry.delete(0, ctk.END)
        self.generated_password_entry.insert(0, password)
        self.generated_password_entry.configure(state="readonly")

    def copy_to_clipboard(self):
        password = self.generated_password_entry.get()
        if password and password != "Selecciona al menos un tipo de carácter":
            self.clipboard_clear()
            self.clipboard_append(password)
            CTkMessagebox.CTkMessagebox(title="Copiado", message="Contraseña copiada al portapapeles.", icon="info")

if __name__ == "__main__":
    app = App()
    app.mainloop()