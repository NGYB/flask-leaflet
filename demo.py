import csv
import sys
import random
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)

BASECOORDS = [-6.2177, 106.8440]

class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude_off = db.Column(db.Float)
    longitude_off = db.Column(db.Float)
    title_ = db.Column(db.String(80))
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'))
    district = db.relationship("District")

    def __init__(self, id, district, lat, lng, t):
        self.id = id
        self.district = district
        self.latitude_off = lat
        self.longitude_off = lng
        self.title_ = t

    def __repr__(self):
        return "<Point %d: Lat %s Lng %s Title %s>" % (self.id, self.latitude_off, self.longitude_off, self.title_)

    @property
    def latitude(self):
        return self.latitude_off + self.district.latitude

    @property
    def longitude(self):
        return self.longitude_off + self.district.longitude

    @property
    def title(self):
        return self.title_


class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __init__(self, id, name, lat, lng):
        self.id = id
        self.name = name
        self.latitude = lat
        self.longitude = lng


@app.route('/')
def index():
    districts = District.query.all()
    return render_template('index.html', districts=districts)


@app.route('/district/<int:district_id>')
def district(district_id):
    points = Point.query.filter_by(district_id=district_id).all()
    coords = [[point.latitude, point.longitude, point.title_] for point in points]
    return jsonify({"data": coords})


def make_random_data(db):
    NDISTRICTS = 1
    NPOINTS = 1
    for did in range(NDISTRICTS):
        district = District(did, "District %d" % did, BASECOORDS[0], BASECOORDS[1])
        db.session.add(district)
        with open("./static/data/data.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    p = Point(line_count, district, float(row[1])-BASECOORDS[0], float(row[2])-BASECOORDS[1], "Withdrawals: "+str(row[0]))
                    print(p)
                    db.session.add(p)
                    line_count += 1
    db.session.commit()





if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'mkdb':
            db.create_all()
            make_random_data(db)
    else:
        app.run(debug=True)
