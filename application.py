import os
import datetime
from calculate_score import *
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import csv
from collections import defaultdict
#from itertools import groupby


PATH = os.path.dirname(__file__)
LEADERBOARD_FILE = os.path.join(PATH, 'leaderboard.csv')
UPLOAD_FOLDER = os.path.join(PATH, 'uploads')
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.secret_key = 'secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Upload size can be maximally 4MB
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.debug = False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

leaderboard_entries = []

def leaderboard():
    leaderboard_dict = defaultdict(list)
    for (score, team, filename) in leaderboard_entries:
        leaderboard_dict[team].append(score)
    leaderboard_dict = {team: max(scores) for team, scores in leaderboard_dict.items()}

    teams_ordered = sorted(leaderboard_dict, key=leaderboard_dict.get, reverse=True)

    return [(i+1, team, leaderboard_dict[team]) for i, team in enumerate(teams_ordered)]

def leaderboard_dict():
    return {entry[1]: entry for entry in leaderboard()}


def init_leaderboard_entries():
    # initialize the leaderboard
    with open(LEADERBOARD_FILE, 'rU+') as f:
        reader = csv.reader(f)
        for row in reader:
            push_local_leaderboard_entry(*row)

def push_local_leaderboard_entry(score, team, filename):
    leaderboard_entries.append((int(score), team, filename))

init_leaderboard_entries()

def sanitize_team(team):
    return team.replace(',', '-').replace('"', '-').replace("'", '-')

def push_leaderboard_entry(score, team, filename):
    with open(LEADERBOARD_FILE, 'a+') as f:
        f.write("%d,%s,%s\n" % (score, team, filename))
        push_local_leaderboard_entry(score, team, filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    entry = None
    previous_entry = None
    if request.method == 'POST':
        file = request.files['file']
        team = sanitize_team(request.form['team'])
        previous_entry = leaderboard_dict()[team] if team in leaderboard_dict() else None
        if file and allowed_file(file.filename):
            now = datetime.datetime.utcnow() + datetime.timedelta(hours=+1)
            filename = "%s_%s" % (team, now.strftime("%d-%m-%y_%H-%M.csv"))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            score = calculate_score(file_path)
            push_leaderboard_entry(score, team, filename)
            entry = leaderboard_dict()[team]

    return render_template('leaderboard.html', leaderboard=leaderboard(),
            entry=entry, previous_entry=previous_entry)

    #'''
    #<!doctype html>
    #<title>Upload new File</title>
    #<h1>Upload new File</h1>
    #<form action="" method=post enctype=multipart/form-data>
    #  <p> Team name:<input type=text name=team>
    #      <input type=file name=file>
    #     <input type=submit value=Upload>
    #</form>
    #''' + str(leaderboard())


if __name__ == '__main__':
    app.run(port=5000)
