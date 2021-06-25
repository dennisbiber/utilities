from flask import Flask
from flask import jsonify
from flask_restful import request  # noqa
from qualifier_endpoints import *  # noqa

app = Flask(__name__)


@app.route("/get_mutual_confirm/<uuid>", methods=["GET"])
def mutal_confrim(uuid):
    return jsonify(query_by_sn(uuid, "mutal_confirm_reults"))


@app.route("/fidelity_stock_confirm/<uuid>", methods=["GET"])
def fid_stock_confirm(uuid):
    return jsonify(query_by_sn(uuid, "fidelity_stock_confirm_results"))


@app.route("/Schwab_stock_confirm/<uuid>", methods=["GET"])
def schw_stock_confirm(uuid):
    return jsonify(query_by_sn(uuid, "Charles_Shwab_stock_confirm_results"))

# returns boolean if the confirmation was valid
@app.route("/get_mutual_confirm/<result>", methods={"GET"})
def mutal_confrim_results(result):
    return jsonify(query_by_result(result, "mutal_confirm_result"))


@app.route("/Schwab_stock_confirm/<result>", methods={"GET"})
def schw_stock_confirm_results(result):
    return jsonify(query_by_result(result, "Fidelity_stock_confirm_result"))


@app.route("/Schwab_stock_confirm/<result>", methods={"GET"})
def schw_stock_confirm_result(result):
    return jsonify(query_by_result(result, "Schwab_stock_confirm_result"))


@app.route("/")
def hello_world():
    return "Purple Hippo Team API"


if __name__ == '__main__':
    app.run(debug=True)
