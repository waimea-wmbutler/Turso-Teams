#===========================================================
# App Creation and Launch
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, server_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now
from app.helpers.images  import image_file


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    with connect_db() as client:
        # Get all the teams from the DB
        sql = "SELECT id, maker FROM Makes ORDER BY maker ASC"
        params = []
        result = client.execute(sql, params)
        teams = result.rows

        # And show them on the page
        return render_template("pages/home.jinja", teams=teams)


#-----------------------------------------------------------
# Team page route - Show details of a single team
#-----------------------------------------------------------
@app.get("/team/<id>")
def show_team_details(id):
    with connect_db() as client:
        # Get the team details from the DB
        sql = "SELECT id, region, maker FROM Maker WHERE id=?"
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so keep going
            team = result.rows[0]

            # Get the team players from the DB
            sql = "SELECT model, price FROM Vehicles WHERE Makes=?"
            params = [id]
            result = client.execute(sql, params)
            players = result.rows

            return render_template("pages/team.jinja", Makes=Makes, Vehicles=Vehicles)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a team, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def add_a_make():
    # Get the data from the form
    maker        = request.form.get("maker")
    region = request.form.get("region")

    # Sanitise the text inputs
    maker = html.escape(maker)
    region = html.escape(region)


    with connect_db() as client:
        # Add the team to the DB
        sql = """
            INSERT INTO Makes (maker, region)
            VALUES (?, ?)
        """
        params = [maker, region]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Maker '{maker}' added", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for adding a team, using data posted from a form
#-----------------------------------------------------------
@app.post("/add-player")
def add_a_car():
    # Get the data from the form

    model  = request.form.get("model")
    price = request.form.get("price")

    # Sanitise the text inputs
    model  = html.escape(name)
    price = html.escape(notes)

    with connect_db() as client:
        # Add the player to the DB
        sql = """
            INSERT INTO players (model, price)
            VALUES (?, ?)
        """
        params = [model, price]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Vehicle '{name}' added", "success")
        return redirect(f"/team/{team}")


#-----------------------------------------------------------
# Route for deleting a team, code given in the route
#-----------------------------------------------------------
@app.get("/delete/<code>")
def delete_a_thing(code):
    with connect_db() as client:
        # Delete the team from the DB
        sql = "DELETE FROM make WHERE code=?"
        params = [code]
        client.execute(sql, params)

        # Go back to the home page
        flash("Team deleted", "success")
        return redirect("/things")
