# Import the dependencies.
from pathlib import Path
from sqlalchemy import create_engine, text, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify
from sqlalchemy import and_
from datetime import datetime, timedelta
import datetime as dt
import pandas as pd
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    given_date = dt.date(2017, 8, 23)
    start_date = given_date - timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    last_12_months_of_precipitation = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date >= start_date).all()
    
    session.close()
    
      # Save the query results as a Pandas DataFrame. Explicitly set the column names
    last_12_months_df = pd.DataFrame(last_12_months_of_precipitation, columns = ['date','prcp'])

    # Convert the query results to a dictionary and Jsonify
    precipitation_dict = {date: prcp for date, prcp in last_12_months_of_precipitation}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    stations_list = session.query(Station.station).all()

    session.close()
    
      # Convert list of tuples into normal list
    normal_stations_list = list(np.ravel(stations_list))
    
    return jsonify(normal_stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    given_date = dt.date(2017, 8, 23)
    start_date = given_date - timedelta(days=365)

    tobs_last_12_months = session.query(Measurement.date, Measurement.tobs).\
        filter(and_(Measurement.station == 'USC00519281', Measurement.date >= start_date)).all()
    
    session.close()
    
     # Convert the query results to a dictionary and Jsonify
    tobs_dict = {str(date): tobs for date, tobs in tobs_last_12_months}
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def startend(start,end=None):

  # Create Start Date Variable
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    if not end:
        day_temp_stats = session.query(func.min(Measurement.tobs).label('lowest_temperature'),
                                  func.max(Measurement.tobs).label('highest_temperature'),
                                  func.avg(Measurement.tobs).label('average_temperature')).\
        filter(Measurement.date >= start_date).all()
        session.close()
        
        day_temp_results = list(np.ravel(day_temp_stats))
        return jsonify(day_temp_results)
        
     # Create End Date Variable
  
    end_date =  dt.datetime.strptime(end, '%Y-%m-%d')

    # Temperature Stats Query
    multi_day_temp_stats = session.query(func.min(Measurement.tobs).label('lowest_temperature'),
                                  func.max(Measurement.tobs).label('highest_temperature'),
                                  func.avg(Measurement.tobs).label('average_temperature')).\
    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    Multi_day_temp_results = list(np.ravel(multi_day_temp_stats))
    session.close()

    return jsonify(Multi_day_temp_results)

if __name__ == '__main__':
    app.run(debug=True)
