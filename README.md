# AI Call Assistant Backend

## Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/ai-call-assistant-backend.git
   cd ai-call-assistant-backend


creazte and activate virtual environment
    python3 -m venv venv
    source venv/bin/activate

INstall dependencies:

    pip install -r requirements.txt

Run the server:
    uvicorn app.main:app --reload



### **D. Regularly Backup Your Virtual Environment**

While virtual environments are generally easy to recreate, it's a good practice to back up critical configurations or `requirements.txt` files to prevent data loss.

### **E. Use Version Control Effectively**

Ensure that your `requirements.txt` and other critical configuration files are tracked in your version control system (e.g., Git) to maintain consistency across different development environments.

---

## **4. Preventive Measures for Future macOS Updates**

To minimize disruptions from future macOS updates, consider the following practices:

1. **Use Python Version Managers:**
   
   - **pyenv:** Allows you to manage multiple Python versions seamlessly.
     ```bash
     brew install pyenv
     ```
   
   - **Setup pyenv:**
     Add the following to your shell configuration file (`~/.zshrc` or `~/.bash_profile`):
     ```bash
     export PYENV_ROOT="$HOME/.pyenv"
     export PATH="$PYENV_ROOT/bin:$PATH"
     eval "$(pyenv init --path)"
     eval "$(pyenv init -)"
     ```
     - **Apply Changes:**
       ```bash
       source ~/.zshrc
       ```
   
   - **Install Specific Python Versions:**
     ```bash
     pyenv install 3.11.4
     pyenv global 3.11.4
     ```
   
   - **Create Virtual Environments with pyenv:**
     ```bash
     pyenv virtualenv 3.11.4 ai-call-assistant-backend
     pyenv activate ai-call-assistant-backend
     ```

2. **Containerize Your Development Environment (Advanced):**
   
   - **Using Docker:**
     - **Create a `Dockerfile`:**
       ```dockerfile
       FROM python:3.11-slim

       WORKDIR /app

       COPY requirements.txt .
       RUN pip install --upgrade pip && pip install -r requirements.txt

       COPY . .

       CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
       ```
     
     - **Build and Run the Docker Container:**
       ```bash
       docker build -t ai-call-assistant-backend .
       docker run -d -p 8000:8000 ai-call-assistant-backend
       ```
     
     - **Benefits:**
       - Environment consistency across different machines.
       - Isolation from host system changes and updates.

3. **Maintain Comprehensive Documentation:**
   
   - Regularly update your `README.md` or other documentation to reflect changes in setup procedures, dependencies, and configurations.

---

## **5. Summary of Fixes**

1. **Activated the Virtual Environment:**
   - Ensured that the virtual environment (`venv`) is active before installing packages.

2. **Installed the Missing `python-jose` Package:**
   - Ran `pip install python-jose` to install the `jose` module.

3. **Updated `requirements.txt`:**
   - Added `python-jose` to `requirements.txt` to track dependencies.

4. **Verified Installation and Backend Functionality:**
   - Confirmed that `python-jose` is installed and that the backend runs without the `ModuleNotFoundError`.

---

## **6. If Problems Persist**

If after following these steps you still encounter issues, consider the following troubleshooting steps:

1. **Double-Check Virtual Environment Activation:**
   
   - Ensure that the virtual environment is activated before running any commands.
   - **Activation Confirmation:** The terminal prompt should start with `(venv)`.

2. **Ensure Correct Python Interpreter:**
   
   - Verify that the virtual environment is using the correct Python version.
   - **Check Python Path:**
     ```bash
     which python
     which pip
     ```
     - **Expected Output:**
       ```
       /Users/carlosalvarez/ai-call-assistant-backend/venv/bin/python
       /Users/carlosalvarez/ai-call-assistant-backend/venv/bin/pip
       ```

3. **Reinstall `python-jose` If Necessary:**
   
   ```bash
   pip uninstall python-jose
   pip install python-jose
