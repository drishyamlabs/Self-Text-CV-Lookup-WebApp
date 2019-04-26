import io
import flask
from flask import Flask, render_template, request
from flask import send_file
import pickle
import pandas as pd
import spacy
import json
import random
import logging
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_fscore_support
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from sklearn.metrics import accuracy_score
import itertools
import textract
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc', 'docx'])

nlp1 = spacy.load('my_model')

def ner_model(text):
	doc_to_test=nlp1(text)
	d={}

	for ent in doc_to_test.ents:
		d[ent.label_]=[]
	for ent in doc_to_test.ents:
		d[ent.label_].append(ent.text)
	for k, v in d.items():
		v.sort()
		d[k] = [item for item, _ in itertools.groupby(v)]
		
	return d
	
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)

app.static_folder = 'static'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.debug = True 

@app.route("/")
def index():
    return flask.render_template('index.html')


def get_file_name(file):
    global fname
    if file and allowed_file(file.filename):
        fname = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
    return(fname)

def read_txt(fname):
    with open(fname, 'r',  encoding="utf8") as file1:
        text = file1.read()
    return(text)

def read_doc_pdf(fname):
    text = textract.process(fname)
    text= text.decode("utf-8")
    return(text)

@app.route("/", methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        fname= get_file_name(file)
        print(fname)
        last= fname.rsplit('.', 1)[-1]
        print(last)
        if last== "txt":
            text= read_txt(fname)
        else:
            text= read_doc_pdf(fname)
        #text= read_txt(fname) 
        dict_fin = ner_model(text)
        return flask.render_template('index.html', result= dict_fin)

if __name__ == "__main__":
    app.run()
