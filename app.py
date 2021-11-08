from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# Database Setup
engine= create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect sqlite database into model
Base = automap_base()

#reflect the tables
Base.prepare(engine, reflect= True)

#save reference to the two tables
measurement= Base.classes.measurement
station= Base.classes.station


app= Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
            f"Let's talk about Hawaiian rain <br/>"
            "<br/>"
            "<br/>"
            f"Available routes: <br/>"
            "<br/>"
            f"/api/v1.0/precipitation"
            "<br/>"
            f"/api/v1.0/stations"
            "<br/>"    
            f"/api/v1.0/tobs"
            "<br/>"
            f"/api/v1.0/start"
            "<br/>"
            f"/api/v1.0/start/end"
            

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session= Session(engine)

    soonest = session.query(measurement.id, measurement.station, func.max(measurement.date), measurement.prcp, measurement.tobs).all()
    soonest_date= soonest[0][2]
    soonest_date= dt.datetime.strptime(soonest_date,'%Y-%m-%d')
    year_ago= soonest_date - dt.timedelta(days=365)
    year_ago= year_ago.strftime('%Y-%m-%d')
    

    results= session.query(measurement.id, measurement.station, measurement.date, measurement.prcp, measurement.tobs).\
                        filter(measurement.date >= year_ago).all()
    temp_data=[ {"Date": result[3]} for result in results]

    session.close()

    return jsonify(temp_data)

@app.route("/api/v1.0/stations")
def stations():
    session= Session(engine)

    results= session.query(station.station, station.name)
    station_list=[ {"Station":result[0], "Station Name": result[1]} for result in results]

    session.close()

    return jsonify(station_list)



@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)

    soonest = session.query(measurement.id, measurement.station, func.max(measurement.date), measurement.prcp, measurement.tobs).all()
    soonest_date= soonest[0][2]
    soonest_date= dt.datetime.strptime(soonest_date,'%Y-%m-%d')
    year_ago= soonest_date - dt.timedelta(days=365)
    year_ago= year_ago.strftime('%Y-%m-%d')


    max_observation=  session.query(measurement.station, func.count(measurement.date)).group_by(measurement.station)\
        .order_by(func.count(measurement.date).desc()).first()

    last_year_results= session.query(measurement.date, measurement.tobs)\
    .filter(measurement.station == max_observation[0]).filter(measurement.date >= year_ago).all()
    
    date_temps_list= [ {"Date": result[0], "Temp": result[1]} for result in last_year_results]

    session.close()
    
    return jsonify(date_temps_list)  

@app.route("/api/v1.0/<start>")
def temperatures_by_start_date(start):
        
    session= Session(engine)

    dt_start= dt.datetime.strptime(start, '%Y-%m-%d')
    str_start= dt_start.strftime('%Y-%m-%d')

    temps_after= session.query(measurement.date, measurement.tobs).filter(measurement.date >= str_start).all()

    max= session.query(measurement.date, func.max(measurement.tobs)).filter( measurement.date >= str_start).all()

    min= session.query(measurement.date, func.min(measurement.tobs)).filter(measurement.date >= str_start).all()

    avg= session.query(measurement.date, func.avg(measurement.tobs)).filter(measurement.date >= str_start).all()

    temp_summary= [{"Start Date": str_start, "Max Temp": max[0][1], "Min Temp": min[0][1], "Average Temp": avg[0][1]}]
    
    session.close()

    return jsonify(temp_summary)

@app.route("/api/v1.0/<start>/<finish>")
def temperatures_between_dates(start,finish):
        
    session= Session(engine)

    dt_start= dt.datetime.strptime(start, '%Y-%m-%d')
    str_start= dt_start.strftime('%Y-%m-%d')

    dt_finish= dt.datetime.strptime(finish,'%Y-%m-%d')
    str_finish= dt_finish.strftime('%Y-%m-%d')

    temps_after= session.query(measurement.date, measurement.tobs).filter(measurement.date >= str_start)\
        .filter(measurement.date <= str_finish).all()

    max= session.query(measurement.date, func.max(measurement.tobs))\
    .filter( measurement.date >= str_start).filter( measurement.date <= str_finish).all()

    min= session.query(measurement.date, func.min(measurement.tobs))\
    .filter( measurement.date >= str_start).filter( measurement.date <= str_finish).all()

    avg= session.query(measurement.date, func.avg(measurement.tobs))\
    .filter(measurement.date >= str_start).filter(measurement.date <= str_finish).all()

    temp_summary_range= [{"Start/End Date": [str_start,str_finish], "Max Temp": max[0][1], "Min Temp": min[0][1], "Average Temp": avg[0][1]}]
    
    session.close()

    return jsonify(temp_summary_range)



if __name__ == "__main__":
    app.run(debug="True")