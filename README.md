
# Secure-Scan

**Secure-Scan** is a secure data classification tool designed to scan and categorize sensitive information across various data types, including Personally Identifiable Information (PII), Protected Health Information (PHI), and Payment Card Information (PCI). Built with Flask and SQLite, this tool automates the process of classifying and storing sensitive data to ensure privacy and compliance. Whether you're handling medical records, financial data, or personal identifiers, Secure-Scan helps safeguard your information scanning techniques.

To ensure portability and easy deployment, Secure-Scan is containerized with Docker, allowing it to run seamlessly in any environment. With the Docker setup, you can quickly deploy, scale, and manage your data classification system without worrying about dependencies or compatibility issues.




## Features

- **File Upload**: Upload CSV files containing data for classification.
- **Data Classification**: Automatically classifies PII, PHI, and PCI data using regular expressions.
- **SQLite Database**: Stores classified data in separate tables for easy retrieval.
- **File History**: Tracks uploaded files and their associated classification results.
- **Result View**: View the classification results for each uploaded file.
- **Delete Functionality**: Remove uploaded files and their classified data from the database.


## Tech Stack

- **Backend**: Python 3.9, Flask
- **Database**: SQLite
- **Frontend**: HTML, Jinja templates
- **Data Classification**: Regular expressions for detecting PII, PHI, PCI data
- **Deployment**: Docker


## Installation

1. Clone the Repository:

```bash
git clone https://github.com/Arch2775/Aurva_assignment.git
cd Aurva_assignment
```

2. Install Dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize the Database:

The database will be initialized automatically when the app runs

```bash
python app.py
```

4. Run the Application

```bash
python app.py
```

The app will be accessible at http://127.0.0.1:5000 

5. **Docker Deployment**:


The application is packaged with Docker for easy deployment. To build and run the app in Docker:

a. open docker and wait for the docker engine to start

b. The Dockerfile defines the steps to build a Docker image for your application. It specifies the base image (like Python), installs dependencies, copies your application code, and sets up the environment inside the container.

c. Build the Docker Image:

The command docker ```bash build -t your_image_name .``` will use the instructions in the Dockerfile to create an image. This image contains your app and all its dependencies.

```bash
docker build -t flask-app .
```

d. Run the Docker Container:

After building the image, you can run the app inside a container using the command

```bash
docker run -p 5001:5000 flask-app
```
 this runs your app inside a container.

Maps port 5001 on your host machine to port 5000 inside the container

 (this allows you to access your app via http://localhost:5001).

Open your browser and go to: http://localhost:5001.

Your Flask app should now be live and running!

1. View Running Containers:

 ```bash
docker ps
 ```
2. Stop a Running Container

```bash
docker stop <CONTAINER_ID>
```

3. Remove Unused Containers and Images

```bash
docker system prune
```

4. Kill a Process Using a Specific Port

find the port 

```bash
netstat -ano | findstr :<PORT>
```

Kill the process

```bash
taskkill /PID <PID> /F
```

5. Stop the Specific Container

```bash
docker stop <CONTAINER_ID>
```

6. Remove the Container

```bash
docker rm <CONTAINER_ID>
```

7. check container logs 

```bash
docker logs <container_id>
```






    
## Usage

Upload CSV Files:

- Go to the Upload page.
- Select a CSV file and upload it.
- The app will classify sensitive data within the file and store the results in the database.

View Classification Results:

- After uploading a file, click on the file name to view detailed classification results for PII, PHI, and PCI data.

Delete Data:

- If you wish to delete a file and its associated classified data, use the Delete button on the results page.

## Contributions

Feel free to fork this repository, submit issues, or make pull requests. All contributions are welcome!




## License

[MIT](https://choosealicense.com/licenses/mit/)

