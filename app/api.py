import os
import pickle
import pandas
import json
from flask import Flask, jsonify, render_template, make_response
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',
        variable_end_string='%%',
    ))

template_dir = os.path.abspath(os.path.dirname(__file__))
app = CustomFlask(__name__, template_folder=template_dir)
CORS(app)
api = Api(app)
parser = reqparse.RequestParser()

parser.add_argument('Atribut', type=dict)

file_model = os.path.abspath(
    os.path.join(__file__, '../../model/model.pkl'))
if os.path.isfile(file_model):
    model = pickle.load(open(file_model, "rb"))
else:
    raise FileNotFoundError

file_penyakit = os.path.abspath(
    os.path.join(__file__, '../../data/penyakit.csv'))
if os.path.isfile(file_penyakit):
    labels = pandas.read_csv(file_penyakit)
else:
    raise FileNotFoundError

file_keluhan = os.path.abspath(
    os.path.join(__file__, '../../data/keluhan.csv'))
if os.path.isfile(file_keluhan):
    indications = pandas.read_csv(file_keluhan)
else:
    raise FileNotFoundError


class Questions(Resource):
    def get(self):
        res_json = json.dumps(indications.to_dict('records'))
        res_json = json.loads(res_json)
        return res_json


class Predict(Resource):
    def post(self):
        args = parser.parse_args()
        x = [list(args['Atribut'].values())]
        y = model.predict(x)
        predicted_labels = y.tolist()
        diseases = [labels.loc[labels['ClassID'] == label]
                    for label in predicted_labels]
        disease = diseases[0]
        index = disease.index[0]
        return [{
            'NameClass': disease['NameClass'][index],
            'PenyebabClass': disease['PenyebabClass'][index]
        }]

class Main(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('index.html', template_dir=template_dir), 200, headers)

api.add_resource(Questions, "/questions")
api.add_resource(Predict, "/predict")
api.add_resource(Main, "/")

if __name__ == "__main__":
    app.run(debug=True)