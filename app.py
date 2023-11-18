from flask import Flask, render_template, jsonify, request
from rdflib import Graph, Namespace,Literal,URIRef
from rdflib.plugins.sparql import prepareQuery
from SPARQLWrapper import SPARQLWrapper, JSON
from flask import render_template, request, url_for
import json

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


if __name__ == '__main__':
    app.run(debug=True)



