from flask import Flask, flash, render_template , jsonify , request , session , redirect, url_for
from numpy import random
from datetime import date
from datetime import datetime
import pymysql
import pymysql.cursors #Variables imported#

app = Flask(__name__)

app.secret_key = 'BookingSession' #Session Secret key

#Database connection#
def db_connect():
  db = pymysql.connect(host="", user="", password="", database="", cursorclass= pymysql.cursors.DictCursor)
  cursor = db.cursor()
  return db , cursor


#Starting Screen#
@app.route("/", methods = ['GET' , 'POST']) 
def welcome_page():



    return render_template('welcomepage.html',)



#Stall book#

@app.route("/book", methods = ['GET' , 'POST']) 
def register_page():
    db_connection = db_connect()
    cursor = db_connection[1]
    db = db_connection[0]

    if request.method=="POST":
        name = request.form["name"]
        date_start = request.form["date_start"]
        date_end = request.form["date_end"]
        size = request.form["size"]
        facilities = request.form["facilities"]
        people = request.form["people"]
        location = request.form["location"]

        d1 = datetime.strptime(str(date_start), "%Y-%m-%d").date()
        d2 = datetime.strptime(str(date_end), "%Y-%m-%d").date()

        total = d2 - d1


        if total.days > 6:
            flash("Error - You can only book up to 6 days")

        if str(size) == "Medium" or "Large" and str(location) == "Inside":
            flash("Error - There can only be small stalls inside")    
        else:
            cursor.execute("INSERT INTO stalls (companyname, datestart, dateend, size, facilities, people, location) VALUES(%s, %s, %s, %s, %s, %s, %s)",(name, date_start, date_end, size, facilities, people, location))
            db.commit()
            session['ID'] = str(name)
            return redirect(url_for("invoice_page"))
    
    return render_template('booking.html')


#Stall Invoice
@app.route("/invoice", methods = ['GET' , 'POST']) 
def invoice_page():
    db_connection = db_connect()
    cursor = db_connection[1]
    person = session["ID"]
    cursor.execute("SELECT * FROM stalls WHERE companyname = %s",(person))
    data = cursor.fetchall()

    bookingid = data[0]["bookingid"]
    company = data[0]["companyname"]
    datestart = data[0]["datestart"]
    datend = data[0]["dateend"]
    size = data[0]["size"]
    facilities = data[0]["facilities"]
    location = data[0]["location"]
    bookingdate = date.today()


    if location =="Outside" and size == "Small":
        stall_costs = 120
    elif location =="Outside" and size == "Medium":
        stall_costs = 150
    elif location =="Outside" and size == "Large":
        stall_costs = 200
    elif location =="Inside" and size == "Small":
        stall_costs = 500


    d1 = datetime.strptime(str(datestart), "%Y-%m-%d").date()
    d2 = datetime.strptime(str(datend), "%Y-%m-%d").date()

    amountdays = d2 - d1

    if facilities =="Both":
        extra_costs = 7.50 * amountdays.days
    elif facilities == "Water Only" or facilities=="Eletricity Only":
        extra_costs = 5 * amountdays.days
    else:
        extra_costs = 0
 
    stall_total = (stall_costs * amountdays.days)
    total_cost = round(((stall_costs * amountdays.days) + extra_costs),2)
    
    session.clear()
    return render_template("invoice_card.html", bookingid = bookingid, stall_total = stall_total, total_cost = total_cost, facilities = facilities, extra_costs = extra_costs, company = company, bookingdate = bookingdate, size = size, location = location, amountdays = amountdays.days, stall_costs = stall_costs )


#Stall Lookup#


@app.route("/lookup", methods = ['GET' , 'POST']) 
def lookup_page():
    db_connection = db_connect()
    cursor = db_connection[1]




    if request.method =="POST":
        bookingid = request.form["bookingidsearch"]
        cursor.execute("SELECT * FROM stalls WHERE bookingid = %s", (bookingid))
        data = cursor.fetchall()

        if data:
            session["ID"] = bookingid
            return redirect(url_for("result_page"))
        else:
            return render_template("index.html")

    


    return render_template('index.html',)


@app.route("/result", methods = ['GET' , 'POST'])
def result_page():

    db_connection = db_connect()
    cursor = db_connection[1]
    bookingid = session["ID"]
    cursor.execute("SELECT * FROM stalls WHERE bookingid = %s",(bookingid))
    data = cursor.fetchall()


    return render_template("viewer.html", bookings = data)



@app.route("/seeall", methods = ['GET' , 'POST'])
def seeall_page():

    db_connection = db_connect()
    cursor = db_connection[1]
    cursor.execute("SELECT * FROM stalls")
    data = cursor.fetchall()


    return render_template("seeall.html", bookings = data)


if __name__ == "__main__":
    app.run()
