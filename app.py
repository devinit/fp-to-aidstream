from flask import Flask, request, render_template, make_response
import webbrowser
import sys
import os
import io
from lxml import etree
from csv import writer as csvwriter
import pdb


# Initialize app, checking if frozen in exe
if getattr(sys, 'frozen', False):
    template_folder = os.path.abspath(os.path.join(sys.executable, '..', 'templates'))
    static_folder = os.path.abspath(os.path.join(sys.executable, '..', 'static'))
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)


# Set "homepage" to index.html
@app.route('/')
def index():
    return render_template('index.html', message="Drag a file to be converted onto this page.")


# Route to convert files
@app.route('/convert', methods=["POST"])
def convert_file():
    fileob = request.files["xmlfile"]
    original_basename, _ = os.path.splitext(fileob.filename)
    tree = etree.parse(fileob)
    root = tree.getroot()

    si = io.StringIO()
    cw = csvwriter(si)
    col_names = ["iati-identifier"]
    cw.writerow(col_names)

    for row in root.getchildren():
        id = [row.xpath("iati-identifier")[0].text]
        cw.writerow(id)

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename={}.csv".format(original_basename)
    output.headers["Content-type"] = "text/csv"
    return output


if __name__ == '__main__':
    webbrowser.open("http://localhost:5000")
    app.run(threaded=True)
