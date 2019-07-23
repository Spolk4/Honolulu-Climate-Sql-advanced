# Now that you have completed your initial analysis, design a Flask API based on the queries that you have just developed.
# Use FLASK to create your routes.
import datetime as dt
import numpy as np
#################################################
# Engine/Session Setup
#################################################
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Routes
#################################################
#2 create an app
app=Flask(__name__)
# Routes
#* `/`
#Home page.
# List all routes that are available:
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
    f"Welcome to my Honolulu Trip Weather data 'Home' page!<br/>"
    f"Available Routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/start<br/>"
    f"/api/v1.0/start_end"
    )

# `/api/v1.0/precipitation`
@app.route("/api/v1.0/precipitation")
def precipitation():
    """ Return a dictionary of the precipitation data and dates """
    #query the Measurements
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date.between('2016-08-23', '2017-08-23')).\
    order_by(Measurement.date).all()
    session.close()
    #Convert the query results to a Dictionary using date as the key and prcp as the value.

    all_precip=[]
    for date, prcp in results:
        precipitation_dict={}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precip.append(precipitation_dict)
    return jsonify(all_precip)

    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    #`/api/v1.0/stations`
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()
    
    #Return a JSON list of stations from the dataset.
    return jsonify(stations)

#`/api/v1.0/tobs`
@app.route("/api/v1.0/tobs")
#query for the dates and temperature observations from a year from the last data point.
def tobs():
    last_yr = dt.date(2017, 8,23) - dt.timedelta(days=365)
    last_data_query = session.query(Measurement.tobs).\
    filter(Measurement.station =='USC00519281').\
        filter(Measurement.date>=last_yr).all()

    tobs_list = list(np.ravel(last_data_query))
    
    return jsonify(tobs_list)
    session.close()
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
# @app.route("/api/v1.0/start")
# def start():
#     start_query= session.query(func.min(Measurement.tobs).label('tmin'), func.avg(Measurement.tobs).label('tavg'), func.max(Measurement.tobs).label('tmax')).\
#         filter(Measurement.date >= start).all()
#     session.close()
#     start_date_list=[]
#     for date in start_query:
#             start_date_dict = {}
#             start_date_dict['tmin'] = date.tmin
#             start_date_dict['tavg'] = date.tavg
#             start_date_dict['tmax'] = date.tmax
#             start_date_list.append(start_date_dict)
#             return jsonify(start_date_list)

# #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
# @app.route("/api/v1.0/start_end")
# def end():
#     end= session.query(func.min(Measurement.tobs).label('tmin'), func.avg(Measurement.tobs).label('tavg'), func.max(Measurement.tobs).label('tmax')).\
#         filter(Measurement.date <= end).all()
#     session.close()
    # end_date_list=[]
    # for date in end_query:
    #         end_date_dict = {}
    #         end_date_dict['tmin'] = date.tmin
    #         end_date_dict['tavg'] = date.tavg
    #         end_date_dict['tmax'] = date.tmax
    #         end_date_list.append(end_date_dict)

@app.route("/api/v1.0/start")
@app.route("/api/v1.0/start_end")

def all_temps(start = None, end= None):
     sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
     
     if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

        # calculate TMIN, TAVG, TMAX with start and stop
        results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)


if __name__=="__main__":
    app.run(debug=True)    