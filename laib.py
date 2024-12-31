import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel, simpledialog
import threading
from tkterm import Terminal
import os
import requests
import re
import json

CONFIG_FILE = "config.json"


def load_config():
    """Carica la configurazione da un file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            messagebox.showerror(
                "Errore", "Errore nel leggere il file di configurazione."
            )
    return {}


def save_config(config):
    """Salva la configurazione in un file."""
    try:
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel salvare la configurazione: {e}")


def configure_endpoint():
    """Apre una finestra di dialogo per configurare l'endpoint."""
    current_config = load_config()
    current_endpoint = current_config.get("lmstudio_endpoint", "")

    new_endpoint = simpledialog.askstring(
        "Configura Endpoint",
        "Inserisci l'endpoint di LMStudio:",
        initialvalue=current_endpoint,
    )

    if new_endpoint:
        current_config["lmstudio_endpoint"] = new_endpoint
        save_config(current_config)
        messagebox.showinfo("Successo", "Endpoint configurato con successo!")


def ask_LLM(query):

    current_config = load_config()
    endpoint = current_config.get("lmstudio_endpoint")

    if not endpoint:
        return "Error: LMStudio endpoint not configured."

    system_prompt = (
        "Context is a real bash shell.\n"
        "Home folder is ~\n"
        "list files with ls\n"
        "If asked command, raw single simplest command possible must be generated, will be executed in a real shell, "
        "written plaintext, no 'if/then/else/ constructions, only simplest commands, no escape chars, no quotes, no preambles, never to be used: '> /dev/null' or '/dev/null 2>&1', no loops.\n"
    )

    request_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{query}"},
    ]

    data = {"messages": request_messages}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"


def load_command_list(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    try:
        with open(filepath, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        messagebox.showerror("File Missing", f"File {filename} is missing.")
        return []


class CommandListEditor(tk.Toplevel):
    def __init__(self, parent, list_type):
        super().__init__(parent)
        self.title(f"Edit {list_type} Commands")
        self.geometry("500x400")
        self.configure(bg="#2E2E2E")

        self.list_type = list_type
        self.file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), f"{list_type}_commands.txt"
        )

        self.command_list = self.load_command_list()

        self.label = tk.Label(
            self, text=f"{list_type.capitalize()} Commands:", bg="#2E2E2E", fg="white"
        )
        self.label.pack(pady=10)

        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE, bg="#3C3C3C", fg="white")
        self.listbox.pack(expand=True, fill="both", padx=10, pady=10)
        self.populate_listbox()

        self.entry = tk.Entry(self, bg="#3C3C3C", fg="white", insertbackground="white")
        self.entry.pack(fill="x", padx=10, pady=5)

        self.button_frame = tk.Frame(self, bg="#2E2E2E")
        self.button_frame.pack(fill="x")

        self.add_button = tk.Button(
            self.button_frame,
            text="Add",
            command=self.add_command,
            bg="#3C3C3C",
            fg="white",
        )
        self.add_button.pack(side="left", padx=5, pady=5)

        self.remove_button = tk.Button(
            self.button_frame,
            text="Remove",
            command=self.remove_command,
            bg="#3C3C3C",
            fg="white",
        )
        self.remove_button.pack(side="left", padx=5, pady=5)

        self.save_button = tk.Button(
            self.button_frame,
            text="Save",
            command=self.save_commands,
            bg="#3C3C3C",
            fg="white",
        )
        self.save_button.pack(side="right", padx=5, pady=5)

    def load_command_list(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                pass

        with open(self.file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]

    def populate_listbox(self):
        self.listbox.delete(0, tk.END)
        for command in self.command_list:
            self.listbox.insert(tk.END, command)

    def add_command(self):
        new_command = self.entry.get().strip()
        if new_command and new_command not in self.command_list:
            self.command_list.append(new_command)
            self.populate_listbox()
            self.entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Command already exists or is invalid.")

    def remove_command(self):
        selected = self.listbox.curselection()
        if selected:
            command = self.listbox.get(selected)
            self.command_list.remove(command)
            self.populate_listbox()
        else:
            messagebox.showwarning("Warning", "No command selected.")

    def save_commands(self):
        with open(self.file_path, "w") as file:
            file.write(
                "\n".join(command.split()[0] for command in self.command_list) + "\n"
            )
        messagebox.showinfo("Saved", "Command saved successfully.")
        self.destroy()


class AIEnhancedTerminalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LAIB# Local AI Bash")
        self.geometry("800x600")
        self.configure(bg="#2E2E2E")
        self.command_history = []
        self.history_index = -1
        self.cache = {}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        help_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#1E1E1E", fg="white")
        settings_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#1E1E1E", fg="white")
        self.menu_bar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(
            label="Edit Whitelist",
            command=lambda: self.open_command_list_editor("whitelisted"),
        )
        settings_menu.add_command(
            label="Edit Blacklist",
            command=lambda: self.open_command_list_editor("blocked"),
        )
        settings_menu.add_command(
            label="Configure LMStudio Endpoint",
            command=configure_endpoint,
        )
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        self.terminal_frame = tk.Frame(self, bg="#1E1E1E")
        self.terminal_frame.grid(row=0, column=0, sticky="nsew")

        self.terminal = Terminal(self.terminal_frame)
        self.terminal.pack(expand=True, fill="both")

        self.query_frame = tk.Frame(self, bg="#1E1E1E")
        self.query_frame.grid(row=1, column=0, sticky="ew")
        self.query_frame.columnconfigure(0, weight=1)
        self.query_frame.columnconfigure(1, weight=0)
        self.query_label = tk.Label(
            self.query_frame,
            text='Generate a command to... (e.g. "change to folder home" - "delete folder \'hi\'")',
            bg="#1E1E1E",
            fg="white",
        )
        self.query_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.query_entry = tk.Entry(
            self.query_frame, bg="#252526", fg="white", insertbackground="white"
        )

        self.query_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.query_entry.bind("<Return>", self.handle_ai_query)
        self.query_entry.bind("<Up>", self.navigate_history)
        self.query_entry.bind("<Down>", self.navigate_history)

        self.reset_cache_button = tk.Button(
            self.query_frame,
            text="Reset Cache",
            command=self.reset_cache,
            bg="#252526",
            fg="white",
        )
        self.reset_cache_button.grid(row=1, column=1, padx=5, pady=5)

    def open_command_list_editor(self, list_type):
        CommandListEditor(self, list_type)

    def handle_ai_query(self, event=None):
        query = self.query_entry.get().strip()
        if not query:
            return

        if not self.command_history or query != self.command_history[-1]:
            self.command_history.append(query)
        self.history_index = len(self.command_history)

        if query in self.cache:
            ai_response = self.cache[query]
        else:
            ai_response = ask_LLM(query).strip()
            self.cache[query] = ai_response

        if ai_response:
            first_line = ai_response.split("\n")[0]
            first_word = first_line.split()[0]

            if first_word == "sudo":
                self.terminal.run_command(
                    "#\n"
                    "# [ERROR] 'sudo' commands are blocked for safety reasons.\n"
                    "# If root permissions are required, consider running this program as root\n# (not recommended).\n"
                )
                return

            dangerous_commands = load_command_list("blocked_commands.txt")
            whitelisted_commands = load_command_list("whitelisted_commands.txt")

            first_line = (
                first_line.replace("> /dev/null 2>&1", "")
                .replace("> /dev/null", "")
                .replace("< /dev/null", "")
                .replace(">/dev/null 2>&1", "")
            )
            # Check for infinite loop patterns with regex
            loop_patterns = [
                r"while\s+true",  # Matches "while true"
                r"for\s+\(\s*;?\s*;?\s*\)",  # Matches "for (;;)" and variations
                r"until\s+false",  # Matches "until false"
                r"while\s+:",  # Matches "while :"
                r":\s+while\s+true",  # Matches ": while true"
                r"while\s+\d+",  # Matches "while 1", "while 42"
                r"while\s+\[\s*.*?\s*\]",  # Matches "while [ condition ]"
                r"while\s+test\s+.*",  # Matches "while test condition"
                r"repeat\s+until\s+false",  # Matches "repeat until false" (Lua style)
                r"while\s+\(\(.*?\)\)",  # Matches "while ((condition))" (Bash arithmetic)
            ]

            # Check if command matches any loop pattern
            if any(re.search(pattern, first_line) for pattern in loop_patterns):
                self.terminal.run_command("# Blocked: infinite loop detected.")
                return

            if any(first_line.startswith(cmd) for cmd in whitelisted_commands):
                self.run_terminal_command(first_line)
            elif any(cmd in first_line for cmd in dangerous_commands):
                self.show_warning_and_edit(first_line)
            else:
                self.run_terminal_command(first_line)

        self.query_entry.delete(0, tk.END)

    def reset_cache(self):
        """Clear the command cache."""
        self.cache.clear()
        messagebox.showinfo("Cache Reset", "Command cache has been cleared.")

    def navigate_history(self, event):
        if self.command_history:
            if event.keysym == "Up" and self.history_index > 0:
                self.history_index -= 1
            elif (
                event.keysym == "Down"
                and self.history_index < len(self.command_history) - 1
            ):
                self.history_index += 1
            self.query_entry.delete(0, tk.END)
            self.query_entry.insert(0, self.command_history[self.history_index])
        return "break"

    def run_terminal_command(self, command):
        threading.Thread(target=self._execute_command, args=(command,)).start()

    def _execute_command(self, command):
        try:
            self.terminal.run_command(command)
        except PermissionError as e:
            self.terminal.run_command("echo ''")
            self.terminal.run_command("#\n")
            self.terminal.run_command(f"# Permission denied: {e}")
        except Exception as e:
            self.terminal.run_command("echo ''")
            self.terminal.run_command("#\n")
            self.terminal.run_command(f"# [ERROR] Command failed: {e}")

    def reset_cache(self):
        messagebox.showinfo("Cache Reset", "Command cache cleared.")

    def show_warning_and_edit(
        self,
        command,
    ):
        warning_window = Toplevel(self)
        warning_window.title("Warning")
        warning_window.geometry("600x300")
        warning_window.configure(bg="#2E2E2E")
        warning_window.transient(self)
        warning_window.grab_set()

        tk.Label(
            warning_window,
            text="AI have generated a blacklisted command.\nPlease review and edit before execution.\n\nESC - to cancel | ENTER - to execute",
            fg="white",
            bg="#2E2E2E",
        ).pack(pady=5)

        command_var = tk.StringVar(value=command)

        command_entry = tk.Entry(
            warning_window,
            textvariable=command_var,
            width=80,
            bg="#3C3C3C",
            fg="white",
            insertbackground="white",
        )
        command_entry.pack(pady=5)
        command_entry.bind("<Return>", lambda e: execute_command())
        command_entry.focus_set()
        command_entry.icursor(len(command))
        first_word = command.split()[0]
        warning_window.bind("<Escape>", lambda e: warning_window.destroy())
        whitelist_var = tk.BooleanVar(value=False)

        def on_whitelist_select():
            if whitelist_var.get():
                confirmation = messagebox.askyesno(
                    "Confirm",
                    f"Adding '{first_word}' to whitelist\nwill bypass future checks.\nProceed?",
                    parent=warning_window,
                )
                if not confirmation:
                    whitelist_var.set(False)

        tk.Checkbutton(
            warning_window,
            text=f"Add '{first_word}' to whitelist",
            variable=whitelist_var,
            bg="#2E2E2E",
            fg="white",
            selectcolor="#3C3C3C",
            command=on_whitelist_select,
        ).pack(pady=5)

        def execute_command():
            modified_command = command_var.get().strip()
            if whitelist_var.get():
                whitelist_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "whitelisted_commands.txt",
                )
                try:
                    with open(whitelist_path, "a") as file:
                        file.write(modified_command.split()[0] + "\n")
                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Failed to add to whitelist: {e}",
                        parent=warning_window,
                    )
            self.run_terminal_command(modified_command)
            warning_window.destroy()

        tk.Button(
            warning_window,
            text="Execute",
            command=execute_command,
            bg="#3C3C3C",
            fg="white",
        ).pack(side=tk.LEFT, padx=10, pady=10)

        tk.Button(
            warning_window,
            text="Cancel",
            command=warning_window.destroy,
            bg="#3C3C3C",
            fg="white",
        ).pack(side=tk.RIGHT, padx=10, pady=10)

    def show_help(self):
        help_window = Toplevel(self)
        help_window.title("User Guide")
        help_window.geometry("800x500")
        help_window.configure(bg="#2E2E2E")

        help_text = (
            "Welcome to LAIB# Local AI Bash\n\n"
            "Main Features:\n"
            "- Generate Bash commands using natural language queries with LMStudio and a local LLM.\n"
            "- Automatically execute AI-generated commands in a real terminal.\n"
            "- Manually enter Bash commands directly into the integrated terminal.\n"
            "- Manage whitelisted (allowed) and blacklisted (blocked) commands.\n"
            "- Review and edit blocked AI-generated commands before execution.\n\n"
            "Requirements:\n"
            "To function properly, this application requires LMStudio installed and running locally at: http://127.0.0.1:1234.\n\n"
            "Suggested LMStudio settings:\n"
            "- Model: bashcopilot-6b-preview\n"
            "- Context Length: 300\n"
            "- Temperature: 0.45\n"
            "- Response Length Limit: 50 tokens\n"
            "- Top-K Sampling: 40\n"
            "- Repeat Penalty: 1.1\n"
            "- Top-P Sampling: 0.95\n"
            "- Minimum P Sampling: 0.05\n\n"
            "How to Use the Application:\n\n"
            "1. Ensure LMStudio is running with the above configuration before starting LAIB#.\n\n"
            "2. Enter Natural Language Queries:\n"
            "   - Use the input box below to describe what you want to do.\n"
            "       - For example, type 'Show files in the current directory.'\n"
            "   - Press Enter to generate the corresponding Bash command.\n"
            "   - Command will execute automatically; if blocked, it will require review.\n\n"
            "3. Manually Enter Commands:\n"
            "   - Write Bash commands directly into the integrated terminal.\n"
            "   - Useful for experienced users or complex commands.\n"
            "   - Outputs will display directly in the terminal window.\n\n"
            "Command Management:\n"
            "- Whitelist: Safe commands that can execute without warnings.\n"
            "- Blacklist: Blocked or dangerous commands requiring review.\n"
            "- Edit both lists through the 'Command Lists' menu in the top bar.\n"
            "- During review, you can choose to add a command to whitelist.\n\n"
            "Advanced Features:\n"
            "- Command Cache:\n"
            "   - Temporarily stores generated and used commands.\n"
            "   - Improves performance during continuous use.\n"
            "   - Use 'Reset Cache' to forget previous AI-generated commands.\n\n"
            "- Review System:\n"
            "   - If a blocked command is generated, a review window appears.\n"
            "   - Edit the command, add it to whitelist, or cancel the action.\n\n"
            "- Command List Editor:\n"
            "   - Access via 'Command Lists' menu to edit white and black lists.\n"
            "   - Add, remove, and save commands from the graphical interface.\n\n"
            "Safety Notes:\n"
            "- Commands starting with 'sudo' are not supported due to tkterm library limitations.\n"
            "- Always verify blocked commands before execution.\n"
            "- Direct input in the terminal bypasses safety checks; use caution.\n\n"
            "Interface Overview:\n"
            "- Integrated Terminal: Displays outputs and allows direct Bash input.\n"
            "- Input Box: Enter natural language queries for command generation.\n"
            "- Reset Cache Button: Clears cache to restore a clean state.\n"
            "- 'Command Lists' Menu: Manage allowed and blocked commands.\n\n"
            "Tips:\n"
            "- Reset the cache if issues arise with AI-generated commands.\n"
            "- Ensure LMStudio is running and properly configured before using this application.\n\n"
            "Thank you for using LAIB# Local AI Bash!"
        )

        text_area = scrolledtext.ScrolledText(
            help_window, wrap=tk.WORD, bg="#3C3C3C", fg="white"
        )
        text_area.insert(tk.END, help_text)
        text_area.configure(state="disabled")
        text_area.pack(expand=True, fill="both", padx=10, pady=10)

    def show_about(self):
        messagebox.showinfo(
            "About", "LAIB# Local AI Bash\nVersion 1.0\nDeveloped by gat"
        )


if __name__ == "__main__":
    app = AIEnhancedTerminalApp()
    app.mainloop()
