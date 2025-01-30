from flask import Flask, request, render_template_string
from PIL import Image
import imagehash
import psycopg2
import io
import json

maxDifference = 3 #the maximum hamming distance
app = Flask(__name__)

# Load database configuration from JSON file
with open('config.json') as config_file:
    config = json.load(config_file)

def twos_complement(hexstr, bits):
    value = int(hexstr,16) #convert hexadecimal to integer

    #convert from unsigned number to signed number with "bits" bits
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

# Function to calculate the phash of an image
def calculate_phash(img):
    imgHash = str(imagehash.phash(img))
    hashInt = twos_complement(imgHash, 64) #convert from hexadecimal to 64 bit signed integer
    return str(hashInt)

# Database connection using loaded configuration
conn = psycopg2.connect(
    database=config["DB_NAME"],
    user=config["DB_USER"],
    password=config["DB_PASSWORD"],
    host=config["DB_HOST"]
)

@app.route('/upload', methods=['POST'])
def upload_photo():
    photo = request.data
    image = Image.open(io.BytesIO(photo))

    phash = calculate_phash(image)
    columns, rows = query_database(phash)

    html_table = generate_html_table(columns, rows, phash)
    return render_template_string(html_table)

def query_database(hashInt):
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM hashes WHERE hash <@ (%s, %s)",(hashInt, maxDifference))
    results = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]

    return column_names, results

def hamming_distance(phash1, phash2):
    """Calculate the Hamming distance between two hashes."""
    return bin(phash1 ^ phash2).count('1')

def calculate_distance(row, hash):
    """Calculate the distance between the calculated phash and the hash from the DB."""
    calculated_phash = int(hash)  # Replace with the actual key for calculated phash
    db_phash = int(row[1])  # Replace with the actual key for DB phash
    return hamming_distance(calculated_phash, db_phash)

def generate_html_table(columns, rows, hash):
    result_table = '''
    <table border="1">
        <tr>
    '''
    # Add column headers to the table
    for col in columns:
        result_table += f'<th>{col}</th>'
    result_table += '<th>Distance</th>'  # Add header for the distance column
    result_table += '</tr>'

    # Add rows to the table
    for row in rows:
        result_table += '<tr>'
        for cell in row:
            if type(cell) == str and cell.startswith('http'):
                cell = f'<a href="{cell}">Link</a>'
            result_table += f'<td'
            if cell is not None:
                result_table += ' style="background:lightgreen;"'
            else:
                result_table += ' style="background:pink;"'
            result_table += f'>{cell}</td>'
        
        # Assuming 'distance' is a value you have for each row
        distance = calculate_distance(row, hash)  # Replace with actual distance calculation
        result_table += f'<td style="background:lightblue;">{distance}</td>'
        
        result_table += '</tr>'

    result_table += '</table>'
    return result_table

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)