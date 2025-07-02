# Fermentation KPI Viewer

**Project History:**
This project began during my time at BTEC, where I initially created fermentation KPI visualizations using static tools. To optimize and modernize the workflow, I rebuilt the project as an interactive dashboard using Plotly Dash, incorporating screenshots of the original visuals and automating the generation of forecast pages and data visualizations.

---

## Technologies Used
- **Python**: Core programming language for all scripts and the dashboard.
- **Dash (by Plotly)**: For building the interactive web dashboard and serving KPI visualizations.
- **Pandas**: For data manipulation, reading/writing CSVs, and preparing data for analysis and visualization.
- **SQLAlchemy**: For database connectivity and ORM, enabling easy loading and saving of data to PostgreSQL.
- **psycopg2-binary**: PostgreSQL database driver for Python, used by SQLAlchemy.
- **Prophet**: For generating time-series forecasts of fermentation KPIs.
- **python-dotenv**: For managing environment variables securely via a `.env` file.
- **Docker**: (Optional) For containerizing the app to ensure consistent deployment across environments.
- **HTML/CSS**: For the generated forecast pages and embedding snapshot images.
- **Jupyter/Static Tools**: (Historical) Used for initial visualizations and screenshots at BTEC.

---

## Cloud & AWS Services
- **Amazon EC2**: Used to host and run the Plotly Dash application in a scalable, cloud-based environment.
- **Amazon RDS (PostgreSQL)**: Provides a managed PostgreSQL database instance for storing, updating, and querying fermentation KPI data and forecasts.
- **Amazon ECR**: Used as a private Docker image registry to store and manage Docker images for the application, enabling seamless deployment to EC2 or other AWS services.

---

## Deploying on AWS: Step-by-Step Directions

### 1. Set Up Amazon RDS (PostgreSQL)
- Create a new PostgreSQL instance in Amazon RDS via the AWS Console.
- Note the endpoint, port, database name, username, and password.
- Make sure your EC2 instance's security group allows inbound/outbound traffic to the RDS instance (typically port 5432).
- Update your `.env` file with the RDS connection string:
  ```
  DB_URL=postgresql://<user>:<password>@<rds-endpoint>:5432/<database>
  ```

### 2. Build and Push Docker Image to Amazon ECR
- Create a new repository in Amazon ECR.
- Authenticate Docker to your ECR registry:
  ```sh
  aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
  ```
- Build your Docker image:
  ```sh
  docker build -t fermentation-app .
  ```
- Tag the image for ECR:
  ```sh
  docker tag fermentation-app:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/fermentation-app:latest
  ```
- Push the image to ECR:
  ```sh
  docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/fermentation-app:latest
  ```

### 3. Launch and Configure EC2 Instance
- Launch an EC2 instance (Amazon Linux 2 or Ubuntu recommended).
- Ensure the security group allows inbound traffic on port 8050 (or your chosen app port).
- SSH into your EC2 instance.
- Install Docker:
  ```sh
  # Amazon Linux 2
  sudo amazon-linux-extras install docker
  sudo service docker start
  sudo usermod -a -G docker ec2-user
  # Ubuntu
  sudo apt-get update && sudo apt-get install -y docker.io
  sudo systemctl start docker
  sudo usermod -aG docker $USER
  ```
- Log out and back in if you changed user groups.
- Authenticate Docker to ECR (repeat the login command from above).
- Pull your image from ECR:
  ```sh
  docker pull <aws_account_id>.dkr.ecr.<region>.amazonaws.com/fermentation-app:latest
  ```

### 4. Configure Environment Variables on EC2
- Create a `.env` file on your EC2 instance with your RDS credentials and any other required variables.
- Or, pass environment variables directly to Docker using `--env-file`:
  ```sh
  docker run -d -p 8050:8050 --env-file .env <aws_account_id>.dkr.ecr.<region>.amazonaws.com/fermentation-app:latest
  ```

### 5. Access the App
- Visit `http://<ec2-public-dns>:8050` in your browser to access the dashboard.

---

## Features
- Interactive dashboard for fermentation KPIs
- Visualizes both bar (aggregate) and time-series metrics
- Forecasts generated using Facebook Prophet
- Data sourced from CSV files and/or a PostgreSQL database (AWS-hosted)
- Auto-generated HTML forecast pages and snapshot images

---

## Directory Structure
```
fermentation/
├── app.py                  # Main Dash app (serves dashboard)
├── bulk-load.py            # Loads CSVs into PostgreSQL (AWS)
├── creatingforecasttables.py # Generates forecast tables in DB
├── generateimagesandpages.py # Generates HTML forecast pages
├── requirements.txt        # Python dependencies
├── Dockerfile              # For containerized deployment
├── .gitignore              # Should include .env
├── .env                    # Environment variables (NOT in repo)
├── fermcsvfiles/           # Source CSV data files
├── pages/                  # Generated HTML forecast pages
├── assets/                 # Snapshot images for visualizations
└── venv/                   # Python virtual environment (optional)
```

---

## Setup Instructions

### 1. Clone the Repository
```sh
git clone <your-repo-url>
cd fermentation
```

### 2. Create and Configure `.env`
Create a `.env` file in the project root with the following variables:
```
DB_URL=postgresql://<user>:<password>@<host>:<port>/<database>
CSV_FOLDER=fermcsvfiles
```
- `DB_URL`: Your AWS PostgreSQL connection string
- `CSV_FOLDER`: Path to your CSV data folder (default: `fermcsvfiles`)

**Important:** `.env` is excluded from git via `.gitignore` for security.

### 3. Set Up a Virtual Environment (Recommended)
```sh
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```sh
pip install -r requirements.txt
```

### 5. Load Data into the Database (Optional)
If you want to refresh the AWS PostgreSQL database with local CSVs:
```sh
python bulk-load.py
```

### 6. Generate Forecast Tables (Optional)
To create/update forecast tables in the database:
```sh
python creatingforecasttables.py
```

### 7. Generate HTML Forecast Pages (Optional)
To generate HTML pages for each KPI forecast:
```sh
python generateimagesandpages.py
```

### 8. Run the Dashboard Locally
```sh
python app.py
```
- The app will be available at [http://localhost:8050](http://localhost:8050)

---

## Docker Usage (Optional)
Build and run the app in a container:
```sh
docker build -t fermentation-app .
docker run -p 8050:8050 --env-file .env fermentation-app
```

---

## Data Files
- Place your CSV files in the `fermcsvfiles/` directory.
- Example files: `Aeration.csv`, `Agitation.csv`, `Batches per year.csv`, etc.

## Generated Files
- Forecast HTML pages: `pages/`
- Snapshot images: `assets/`

---

## Security Notes
- **Never commit your `.env` file or credentials to version control.**
- `.env` is already in `.gitignore`.
- If you accidentally pushed `.env`, see [GitHub's guide](https://docs.github.com/en/github/authenticating-to-github/removing-sensitive-data-from-a-repository) to remove it from history.

---

## Dependencies
Key Python packages:
- dash, Flask, pandas, numpy, plotly, SQLAlchemy, psycopg2-binary, python-dotenv, prophet

See `requirements.txt` for the full list.

---

## License
Specify your license here.

---

## Contact
For questions or contributions, open an issue or pull request. 