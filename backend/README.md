# Project Setup

### 1. Create a `.env` File

Create a file named `.env` in the root of your project directory and add the following line:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/db_name
```

Replace the `username`, `password`, and `db_name` with your actual MySQL database credentials.

### 2. Install Required Dependencies

Run the following command to install all the required dependencies listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This will install all the necessary packages for the project to run.
