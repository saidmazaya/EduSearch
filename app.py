from flask import Flask, render_template, jsonify
from rdflib import Graph, Namespace,Literal,URIRef
from rdflib.plugins.sparql import prepareQuery
from SPARQLWrapper import SPARQLWrapper, JSON
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

@app.route('/')
def home():
    data_to_pass = {
        'judul': 'Contoh Aplikasi Flask',
        'pesan': 'Selamat datang di aplikasi Flask sederhana!',
        'items_list': ['Item 1', 'Item 2', 'Item 3']
    }
    return render_template('home.html', data=data_to_pass)

@app.route('/index')
def index():
    all_query = run_query(query_all)

    return render_template('index.html', all_query=all_query)

@app.route('/topic')
def topic():
    return render_template('topics.html')


if __name__ == '__main__':
    app.run(debug=True)




