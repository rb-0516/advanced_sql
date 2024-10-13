# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# # reflect an existing database into a new model
Base = automap_base()
# # reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)
# #################################################
# # Flask Setup
# #################################################
app = Flask(__name__)


# Define your routes here...
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def get_prcp_data():
    # Calculate the date one year from the last date in data set.
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    data_precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date>=previous_year).all()
    
    results = {}
    for data in data_precipitation:
        results[data[0]]=data[1] 

    return jsonify(results)

@app.route("/api/v1.0/stations")
def get_stations():
    # List all stations in data set.
    total_stations = session.query(station.station).all()
    
    station_list = list(np.ravel(total_stations))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def get_tobs():
    # Get all dates and temps for the most-active station for the previous year
    # Calculate previous year
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Perform a query for the temp observations
    results = session.query(measurement.tobs).filter(measurement.station=='USC00519281').filter(measurement.date>=previous_year).all()
   
    tobs_list = list(np.ravel(results))
   
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def get_start_data(start):
    
    # Convert start and end dates to datetime objects
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
      
    except ValueError:
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400
    
    sel = [func.min(measurement.tobs), 
        func.avg(measurement.tobs), 
        func.max(measurement.tobs)]

    results = session.query(*sel).filter(measurement.date > start_date).all()

    results_list = list(np.ravel(results))

    return jsonify(results_list)

@app.route("/api/v1.0/<start>/<end>")
def get_start_end_data(start,end):
    
    # Convert start and end dates to datetime objects
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
      
    except ValueError:
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400
    
    sel = [func.min(measurement.tobs), 
        func.avg(measurement.tobs), 
        func.max(measurement.tobs)]

    results = session.query(*sel).filter(measurement.date > start_date).\
            filter(measurement.date <= end_date).all()

    results_list = list(np.ravel(results))

    return jsonify(results_list)

# print(app.url_map)


# #################################################
# # Flask Routes
# #################################################

if __name__ == '__main__':
    app.run(debug=True)
# Close Session
session.close()