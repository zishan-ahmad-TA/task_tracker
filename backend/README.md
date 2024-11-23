# Project Setup

### 1. Create a `.env` File

Create a file named `.env` in the root of your project directory and add the following line:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/db_name
```

Replace `username`, `password`, and `db_name` with your actual MySQL database credentials.

---

### 2. Project Setup Guide

This guide explains how to install the necessary dependencies for the project using the `Pipfile.lock` with `pipenv`.

#### Prerequisites

1. **Python**: Ensure Python is installed (preferably Python 3.7 or later).  
2. **pip**: Ensure `pip` (Python package manager) is installed.

---

#### Installation Steps

1. **Install pipenv**  
   Use `requirements.txt` to install `pipenv` as a dependency. Run the following command:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Dependencies from `Pipfile.lock`**  
   Once `pipenv` is installed, install the dependencies listed in `Pipfile.lock` using:
   ```bash
   pipenv install --dev
   ```
   The `--dev` flag ensures that both regular and development dependencies are installed. If development dependencies are not needed, run:
   ```bash
   pipenv install
   ```
Here's how you can add instructions to activate the virtual environment when using `pipenv` in your setup guide:

---

3. **Activate the Virtual Environment**

After installing the dependencies, activate the virtual environment created by `pipenv` to ensure all commands and scripts run in an isolated environment.

1. **Activate the Virtual Environment**  
   Run the following command:
   ```bash
   pipenv shell
   ```

   This will activate the virtual environment, and you'll see the environment name as part of your shell prompt.

2. **Deactivate the Virtual Environment**  
   When you're done working in the virtual environment, you can deactivate it by simply running:
   ```bash
   exit
   ```