from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import csv
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'aurva_proj'
DATABASE = "data.db"


# Initialize database
# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS PII')
    cursor.execute('DROP TABLE IF EXISTS PHI')
    cursor.execute('DROP TABLE IF EXISTS PCI')
    cursor.execute('DROP TABLE IF EXISTS ScannedFiles')
    
  
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS PII (
            ID INTEGER,
            Name TEXT,
            PAN_SSN TEXT,
            Classification TEXT,
            Sensitive_Info TEXT,  
            UploadTime TEXT
        )
    ''')
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS PHI (
            ID INTEGER,
            Name TEXT,
            Medical_Record_Number TEXT,
            Test_Results TEXT,
            Health_Insurance_Info TEXT,
            Insurance_Coverage_Desc TEXT,
            Classification TEXT,
            Sensitive_Info TEXT,  
            UploadTime TEXT
        )
    ''')
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS PCI (
            ID INTEGER,
            Name TEXT,
            Credit_Card_Number TEXT,
            Classification TEXT,
            Sensitive_Info TEXT,  
            UploadTime TEXT
        )
    ''')
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS ScannedFiles (
            DocID INTEGER PRIMARY KEY AUTOINCREMENT,
            DocName TEXT,
            UploadTime TEXT
        )
    ''')
    conn.commit()
    conn.close()




# Classification Logic
# Classification Logic
def classify_data(file_path, file_name):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Record file upload metadata
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('INSERT INTO ScannedFiles (DocName, UploadTime) VALUES (?, ?)', (file_name, upload_time))
        conn.commit()
        
        with open(file_path, "r") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) < 3:  # Skip rows with insufficient columns
                    continue
                
                ID, Name = row[0], row[1]
                PAN_Card_Number, SSN = None, None
                Medical_Record_Number, Test_Results = None, None
                Health_Insurance_Info, Insurance_Coverage_Desc = None, None
                Credit_Card_Number = None
                sensitive_info = row[-1]  # The last item in the row is the sensitive info

                # PII Classification
                if len(row) >= 3 and re.match(r"[A-Z]{5}[0-9]{4}[A-Z]", row[2]):
                    PAN_Card_Number = row[2]
                    cursor.execute(
                        '''
                        INSERT INTO PII (ID, Name, PAN_SSN, Classification, Sensitive_Info, UploadTime) 
                        VALUES (?, ?, ?, 'PII', ?, ?)
                        ''', 
                        (ID, Name, PAN_Card_Number, sensitive_info, upload_time)
                    )
                elif len(row) >= 3 and re.match(r"\d{3}-\d{2}-\d{4}", row[2]):
                    SSN = row[2]
                    cursor.execute(
                        '''
                        INSERT INTO PII (ID, Name, PAN_SSN, Classification, Sensitive_Info, UploadTime) 
                        VALUES (?, ?, ?, 'PII', ?, ?)
                        ''', 
                        (ID, Name, SSN, sensitive_info, upload_time)
                    )

                # PHI Classification
                elif len(row) >= 6 and re.match(r"MR\d+", row[2]):
                    Medical_Record_Number = row[2]
                    Test_Results = row[3]
                    Health_Insurance_Info = row[4]
                    Insurance_Coverage_Desc = row[5]
                    cursor.execute(
                        '''
                        INSERT INTO PHI (ID, Name, Medical_Record_Number, Test_Results, 
                        Health_Insurance_Info, Insurance_Coverage_Desc, Classification, Sensitive_Info, UploadTime) 
                        VALUES (?, ?, ?, ?, ?, ?, 'PHI', ?, ?)
                        ''', 
                        (ID, Name, Medical_Record_Number, Test_Results, 
                         Health_Insurance_Info, Insurance_Coverage_Desc, sensitive_info, upload_time)
                    )

                # PCI Classification
                elif len(row) >= 3 and re.match(r"\d{4}-\d{4}-\d{4}-\d{4}", row[2]):
                    Credit_Card_Number = row[2]
                    cursor.execute(
                        '''
                        INSERT INTO PCI (ID, Name, Credit_Card_Number, Classification, Sensitive_Info, UploadTime) 
                        VALUES (?, ?, ?, 'PCI', ?, ?)
                        ''', 
                        (ID, Name, Credit_Card_Number, sensitive_info, upload_time)
                    )

        conn.commit()
    except Exception as e:
        print(f"Error occurred during classification: {e}")
    finally:
        conn.close()





# Routes
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            try:
                # Save the uploaded file and classify it
                os.makedirs("data", exist_ok=True)
                file_path = os.path.join("data", file.filename)
                file.save(file_path)
                classify_data(file_path, file.filename)
                flash("File uploaded and classified successfully!", 'success')
            except Exception as e:
                flash(f"Error processing file: {e}", 'danger')
        else:
            flash("No file selected. Please upload a file.", 'warning')
        return redirect(url_for('upload'))
    
    # Fetch file metadata from the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT DocID, DocName, UploadTime FROM ScannedFiles")
    files_data = cursor.fetchall()
    conn.close()
    
    return render_template('upload.html', files_data=files_data)


@app.route('/result/<int:doc_id>')
def result(doc_id):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Fetch classification data
        cursor.execute("SELECT * FROM PII WHERE ID IN (SELECT ID FROM ScannedFiles WHERE DocID = ?)", (doc_id,))
        pii_data = cursor.fetchall()

        cursor.execute("SELECT * FROM PHI WHERE ID IN (SELECT ID FROM ScannedFiles WHERE DocID = ?)", (doc_id,))
        phi_data = cursor.fetchall()

        cursor.execute("SELECT * FROM PCI WHERE ID IN (SELECT ID FROM ScannedFiles WHERE DocID = ?)", (doc_id,))
        pci_data = cursor.fetchall()

        # Fetch upload time
        cursor.execute("SELECT UploadTime FROM ScannedFiles WHERE DocID = ?", (doc_id,))
        upload_time = cursor.fetchone()
        upload_time = upload_time[0] if upload_time else "Unknown"

        return render_template(
            'result.html', 
            pii_data=pii_data, 
            phi_data=phi_data, 
            pci_data=pci_data, 
            doc_id=doc_id, 
            upload_time=upload_time
        )
    except Exception as e:
        flash(f"Error fetching results: {e}", 'danger')
        return redirect(url_for('upload'))
    finally:
        conn.close()

@app.route('/delete/<int:doc_id>', methods=['POST'])
def delete(doc_id):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Get the document name from ScannedFiles
        cursor.execute("SELECT DocName FROM ScannedFiles WHERE DocID = ?", (doc_id,))
        doc_name = cursor.fetchone()
        if not doc_name:
            flash("File not found in database.", 'danger')
            return redirect(url_for('upload'))
        
        doc_name = doc_name[0]

        # Delete rows from classification tables based on DocID
        cursor.execute("DELETE FROM PII WHERE UploadTime IN (SELECT UploadTime FROM ScannedFiles WHERE DocID = ?)", (doc_id,))
        cursor.execute("DELETE FROM PHI WHERE UploadTime IN (SELECT UploadTime FROM ScannedFiles WHERE DocID = ?)", (doc_id,))
        cursor.execute("DELETE FROM PCI WHERE UploadTime IN (SELECT UploadTime FROM ScannedFiles WHERE DocID = ?)", (doc_id,))

        # Delete the file entry from ScannedFiles
        cursor.execute("DELETE FROM ScannedFiles WHERE DocID = ?", (doc_id,))

        # Commit the changes
        conn.commit()
        flash(f"File '{doc_name}' and its data have been deleted successfully!", 'success')
    except Exception as e:
        flash(f"Error deleting file: {e}", 'danger')
    finally:
        conn.close()

    return redirect(url_for('upload'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
