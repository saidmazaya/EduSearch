from flask import Flask, render_template, jsonify, request
from rdflib import Graph, Namespace,Literal,URIRef
from rdflib.plugins.sparql import prepareQuery
from SPARQLWrapper import SPARQLWrapper, JSON
from flask import render_template, request, url_for
import json
import math

app = Flask(__name__)
# Deklarasi Namespace
INSTANSI_SUMUT = Namespace("https:///schema/Instansi_sumut#")
PREFIXES = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX instansi: <https:///schema/Instansi_sumut#>
"""

# Fungsi untuk menjalankan query SPARQL
def run_query(query):
    sparql = SPARQLWrapper("http://localhost:3030/tubes/query")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

def get_bentuk_pendidikan_classification():
    query = f"""
    {PREFIXES}

    SELECT DISTINCT ?bentukPendidikan
    WHERE {{
      ?individu instansi:namaSekolah ?namaSekolah ;
                instansi:kindOf ?bentukPendidikan .
      FILTER (
        !CONTAINS(STR(?bentukPendidikan), "SPK")
      )
    }}
    """
    results = run_query(query)
    return [{'bentukPendidikan': result['bentukPendidikan']['value']} for result in results]

# Query SPARQL untuk mendapatkan informasi tentang TK Ar-Rayhan School
query_string = f"""
{PREFIXES}

SELECT ?subject ?predicate ?object
WHERE {{
    ?subject instansi:namaSekolah "TK AR-RAYHAN SCHOOL" .
    ?subject ?predicate ?object .
}}          
"""

query_all = f"""
{PREFIXES}

SELECT DISTINCT  ?namaSekolah ?npsn ?akreditasi ?bentukPendidikan ?kecamatan 
WHERE {{
    OPTIONAL {{
        ?individu instansi:namaSekolah ?namaSekolah ;
                instansi:NPSN ?npsn ;
                instansi:akreditasi ?akreditasi ;
                instansi:kindOf ?bentukPendidikan ;
                instansi:locatedIn ?kecamatan .
    }}
}}
"""

    # nama , NPSN, bentuk pendidikan, Kecamatan, action
# 

@app.route('/tk')
def tk_ar_rayhan_info():
    results = run_query(query_string)
    return render_template('tk_info.html', results=results)

@app.route('/kecamatan')
def kecamatan():
    # Add any logic or data retrieval needed for the kecamatan page
    return render_template('kecamatan.html')

@app.route('/kecamatan/<kecamatan>')
def kecamatan_detail(kecamatan):
    # Logic to handle the kecamatan parameter and modify SPARQL query
    query_by_kecamatan = f"""
    {PREFIXES}

    SELECT DISTINCT *
        WHERE {{
            BIND("https:///schema/Instansi_sumut#Kecamatan_{kecamatan}" AS ?targetKecamatan)
            OPTIONAL {{
                ?individu instansi:namaSekolah ?namaSekolah ;
                    instansi:NPSN ?npsn ;
                    instansi:akreditasi ?akreditasi ;
                    instansi:kindOf ?bentukPendidikan ;
                    instansi:locatedIn ?targetKecamatan .
            }}
        }}
    """

    results = run_query(query_by_kecamatan)
    bentuk_pendidikan_classification = get_bentuk_pendidikan_classification()

    return render_template('kecamatan.html', results=results, selectedKecamatan=kecamatan, bentuk_pendidikan_classification=bentuk_pendidikan_classification)


@app.route('/')
def home():
    data_to_pass = {
        'judul': 'Contoh Aplikasi Flask',
        'pesan': 'Selamat datang di aplikasi Flask sederhana!',
        'items_list': ['Item 1', 'Item 2', 'Item 3']
    }
    return render_template('home.html', data=data_to_pass)

# Fungsi route '/index'
@app.route('/index')
def index():
    keyword = request.args.get('keyword', default='', type=str)
    bentuk_pendidikan = request.args.get('bentukPendidikan', default='', type=str)

    # Get bentuk_pendidikan_classification for dropdown
    bentuk_pendidikan_classification = get_bentuk_pendidikan_classification()

    # SPARQL query with filter for bentukPendidikan if available
    query_all_a = f"""
        {PREFIXES}

        SELECT DISTINCT ?namaSekolah ?npsn ?akreditasi ?bentukPendidikan ?kecamatan
        WHERE {{
            ?individu instansi:namaSekolah ?namaSekolah ;
                    instansi:NPSN ?npsn ;
                    instansi:akreditasi ?akreditasi ;
                    instansi:kindOf ?bentukPendidikan ;
                    instansi:locatedIn ?kecamatan .

            FILTER(
                regex(STR(?namaSekolah), "{keyword}", "i") ||
                regex(STR(?npsn), "{keyword}", "i")
            )

            {f'FILTER(?bentukPendidikan = "{bentuk_pendidikan}")' if bentuk_pendidikan else ''}

        }}
    """

    if keyword or bentuk_pendidikan:
        results = run_query(query_all_a)
        return render_template('index.html', results=results, keyword=keyword, bentuk_pendidikan_classification=bentuk_pendidikan_classification, selectedBentuk=bentuk_pendidikan)
    else:
        # Include this line to get all bentuk pendidikan if no filter is applied
        all_query = run_query(query_all)
        return render_template('index.html', all_query=all_query, keyword=keyword, bentuk_pendidikan_classification=bentuk_pendidikan_classification, selectedBentuk=bentuk_pendidikan)

@app.route('/detail/<npsn>')
def detail(npsn):
    # SPARQL query to retrieve details for the specified NPSN
    query_detail = f"""
    {PREFIXES}

    SELECT DISTINCT *
    WHERE {{
        BIND("{npsn}" AS ?targetNPSN)
        OPTIONAL {{
            ?individu instansi:NPSN ?targetNPSN ;
                    instansi:namaSekolah ?namaSekolah ;
                    instansi:alamat ?alamat ;
                    instansi:lintang ?lintang ;
                    instansi:Status ?status ;
                    instansi:kabupaten ?kabupaten ;
                    instansi:bujur ?bujur ;
                    instansi:tanggalPendirian ?tanggalPendirian ;
                    instansi:akreditasi ?akreditasi ;
                    instansi:linkSekolah ?linkSekolah ;
                    instansi:kindOf ?bentukPendidikan ;
                    instansi:locatedIn ?kecamatan .
        }}
    }}
    """

    # Execute the SPARQL query
    data_detail = run_query(query_detail)

    # Pass the results to the template
    return render_template('detail.html', npsn=npsn, data=data_detail)

# Haversine formula to calculate distance between two sets of coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Radius of the Earth in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Vincenty Formulae
def vincenty_distance(lat1, lon1, lat2, lon2):
    # WGS-84 ellipsoidal parameters
    a = 6378137.0  # semi-major axis in meters
    f = 1 / 298.257223563  # flattening
    b = (1 - f) * a  # semi-minor axis

    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    U1 = math.atan((1 - f) * math.tan(lat1))
    U2 = math.atan((1 - f) * math.tan(lat2))
    lon_diff = lon2 - lon1
    lambda_old = lon_diff
    lambda_new = 2 * math.pi

    while abs(lambda_new - lambda_old) > 1e-12:
        sin_sigma = math.sqrt((math.cos(U2) * math.sin(lon_diff))**2 + (math.cos(U1) * math.sin(U2) - math.sin(U1) * math.cos(U2) * math.cos(lon_diff))**2)
        cos_sigma = math.sin(U1) * math.sin(U2) + math.cos(U1) * math.cos(U2) * math.cos(lon_diff)
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = math.cos(U1) * math.cos(U2) * math.sin(lon_diff) / math.sin(sigma)
        cos_sq_alpha = 1 - sin_alpha**2
        cos_2sigma_m = cos_sigma - 2 * math.sin(U1) * math.sin(U2) / cos_sq_alpha
        C = f / 16 * cos_sq_alpha * (4 + f * (4 - 3 * cos_sq_alpha))
        lambda_old = lambda_new
        lambda_new = lon_diff + (1 - C) * f * sin_alpha * (sigma + C * math.sin(sigma) * (cos_2sigma_m + C * math.cos(sigma) * (-1 + 2 * cos_2sigma_m**2)))

    u_sq = cos_sq_alpha * (a**2 - b**2) / (b**2)
    A = 1 + u_sq / 16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
    B = u_sq / 1024 * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))
    delta_sigma = B * math.sin(sigma) * (cos_2sigma_m + B / 4 * (math.cos(sigma) * (-1 + 2 * cos_2sigma_m**2) - B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma**2) * (-3 + 4 * cos_2sigma_m**2)))

    distance = b * A * (sigma - delta_sigma)

    return distance

@app.route('/terdekat', methods=['GET', 'POST'])
def terdekat():
    # SPARQL query to retrieve details for the specified NPSN
    query_terdekat = f"""
    {PREFIXES}

    SELECT DISTINCT  ?namaSekolah ?npsn ?akreditasi ?bentukPendidikan ?kecamatan ?lintang ?bujur
    WHERE {{
        OPTIONAL {{
            ?individu instansi:namaSekolah ?namaSekolah ;
                    instansi:NPSN ?npsn ;
                    instansi:lintang ?lintang ;
                    instansi:bujur ?bujur ;
                    instansi:akreditasi ?akreditasi ;
                    instansi:kindOf ?bentukPendidikan ;
                    instansi:locatedIn ?kecamatan .
        }}
    }}
    """

    user_latitude_str = request.args.get('latitude', '0')
    user_longitude_str = request.args.get('longitude', '0')

    try:
        user_latitude = float(user_latitude_str)
        user_longitude = float(user_longitude_str)
    except ValueError:
        # Handle the case where parsing to float fails
        return "Invalid latitude or longitude", 400
    
        # Print the values for debugging
    print(f"User Latitude: {user_latitude}")
    print(f"User Longitude: {user_longitude}")

    # Assuming you have a function to query the SPARQL endpoint for schools
    # Replace this with your actual SPARQL query and logic
    data_terdekat = run_query(query_terdekat)

    # Calculate distance for each school and add it to the data
    for school in data_terdekat:
        school_latitude_str = school["lintang"]["value"]
        school_longitude_str = school["bujur"]["value"]

        try:
            school_latitude = float(school_latitude_str)
            school_longitude = float(school_longitude_str)
        except ValueError:
            # Handle the case where parsing to float fails
            school["distance"] = None
            continue

        distance = haversine(user_latitude, user_longitude, school_latitude, school_longitude)
        school["distance"] = distance

    # Execute the SPARQL query
    bentuk_pendidikan_classification = get_bentuk_pendidikan_classification()

    # Pass the results to the template
    return render_template('terdekat.html', data=data_terdekat, bentuk_pendidikan_classification=bentuk_pendidikan_classification)

if __name__ == '__main__':
    app.run(debug=True)



