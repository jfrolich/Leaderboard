import os
import datetime
from calculate_score import *
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import csv
from collections import defaultdict
#from itertools import groupby

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.secret_key = 'secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Upload size can be maximally 4MB
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.debug = True

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

def init_leaderboard_entries():
    # initialize the leaderboard
    with open('leaderboard.csv', 'rU+') as f:
        reader = csv.reader(f)
        for row in reader:
            push_local_leaderboard_entry(*row)

def push_local_leaderboard_entry(score, team, filename):
    leaderboard_entries.append((int(score), team, filename))

init_leaderboard_entries()

def sanitize_team(team):
    return team.replace(',', '-').replace('"', '-').replace("'", '-')

def push_leaderboard_entry(score, team, filename):
    with open('leaderboard.csv', 'a+') as f:
        f.write("%d,%s,%s\n" % (score, team, filename))
        push_local_leaderboard_entry(score, team, filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        team = sanitize_team(request.form['team'])

        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)

            now = datetime.datetime.utcnow() + datetime.timedelta(hours=+1)
            filename = "%s_%s" % (team, now.strftime("%d-%m-%y_%H-%M.csv"))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            score = calculate_score(file_path)
            push_leaderboard_entry(score, team, filename)
    return render_template('leaderboard.html', leaderboard=leaderboard())

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
