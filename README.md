# LAIB# Local AI Bash

## Overview
**LAIB# Local AI Bash** is an interactive terminal application that integrates a local AI model for natural language-based Bash command generation. It includes features like whitelisting, blacklisting, and manual command review to ensure safety and usability.

### Key Features
- Generate Bash commands using natural language queries.
- Uses local LLM Models (LMStudio https://lmstudio.ai/ required).
- Automatically execute generated commands in a real terminal.
- Review and edit AI-generated commands before execution.
- Manage whitelisted (allowed) and blacklisted (blocked) commands.
- Infinite loops and common 'bad' commands protection.
- Integrated terminal for manual command entry.
- Customizable menus and search: Access menu for customization, command list management, and searching through terminal output. Additionally, a context menu is available in terminal by right-clicking.

---

## Requirements
To use this application, ensure you have:

1. **Python 3.8+** installed on your system.
2. **LMStudio** running locally to interact with the AI model (https://lmstudio.ai/).
3. A LLM Model downloaded from LMStudio, better if trained on bash commands (see suggested below).

### Suggested LMStudio Configuration
- LLM Model: `bashcopilot-6b-preview`
- Context Length: `300`
- Temperature: `0.45 - 0.5`
- Response Length Limit: `50 tokens`
- Top-K Sampling: `40`
- Repeat Penalty: `1.1`
- Top-P Sampling: `0.95`
- Minimum P Sampling: `0.05`

---

## Installation

1. **Clone the Repository**
```bash
$ git clone https://github.com/davidegat/LAIB-Local-AI-Bash.git
$ cd LAIB-Local-AI-Bash
```

2. **Set Up a Virtual Environment (Optional)**
```bash
$ python3 -m venv venv
$ source venv/bin/activate
```

3. **Install Required Libraries**
Manually install required libraries using the following command:
```bash
$ pip install tkinter requests tkterm
```

4. **Install LMStudio**
- Download and install LMStudio.
- Download and load the suggested model.
- Configure LMStudio to run at `http://127.0.0.1:1234`.
- Dowload the suggested model from LMStudio.

---

## Usage

### Starting the Application
Ensure LMStudio is running before starting the application. Then execute:
```bash
$ python laib.py
```

### Interface Overview
1. **Terminal Frame**: Interactive terminal for direct Bash commands and output display.
2. **Query Box**: Input natural language queries to generate Bash commands.
3. **Menu Bar**:
   - **Help**: Access user guide and about section.
   - **Command Lists**: Edit whitelist and blacklist for commands.
4. **Reset Cache Button**: Clears AI command cache.
5. **Customizable Menus and Search**:
   - Use top-right menu to customize behavior, manage command lists, and search through terminal output.
   - Access a context menu in terminal by right-clicking.

### Example Workflow
1. Enter a query in the query box, e.g., `Show files in current dir`
2. AI will generate a Bash command, which will be checked against whitelist/blacklist.
3. If approved, command is executed automatically in terminal.
4. If blocked, a review window allows you to edit or approve the command.

### Command Management
- **Whitelist**: Commands that bypass review and execute directly.
- **Blacklist**: Commands requiring review before execution.
- Access these lists from `Command Lists` menu.

---

## Advanced Features

### Command Review
When a blocked command is generated:
1. A review window appears, displaying the command.
2. Edit the command or approve it for execution.
3. Optionally, add command to whitelist for future use.

### Command Cache
- Temporarily stores generated commands for faster reuse.
- Use `Reset Cache` button to clear this cache.

### Safety Notes
- Commands starting with `sudo` are not supported by tkterm library and are blocked for safety.
   - Run this software as root instead (not recommended).
- Direct input in terminal bypasses safety checks; use with caution.
- Supported Shells: Currently, only Bash is supported. Other interpreters or shells you will select by terminal menu may not function correctly with this application.

---

## File Structure

```plaintext
LAIB-Local-AI-Bash/
├── laib.py                   # Main application file
├── LICENSE                   # License file
├── README.md                 # Project documentation
├── whitelisted_commands.txt  # Whitelisted commands
└── blocked_commands.txt      # Blacklisted commands

```

---

## Troubleshooting

### Common Issues
1. **AI not responding**: Ensure LMStudio is running and accessible at `http://127.0.0.1:1234`, check if model is loaded and its settings.
2. **Command not executing**: Check if command is in blacklist.
3. **Sudo commands not allowed**: These are generally blocked, run software as root if needed.

### Reset Cache
Click `Reset Cache` to clear cached commands.

---

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Submit a pull request with a detailed explanation of changes.

---

## License
This project is Open Source. See the [LICENSE](LICENSE) file for details.

---

Software is provided as-is. By using it, you accept to take all responsibility for any damage of any kind this software may cause to your data, device(s), firm, corporation, shop, family, friends, whole life, belongings, backyard, dignity, and other moral and psychological stuff, your body or your cats'.