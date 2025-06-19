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
        sql = "SELECT code, name FROM teams ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        teams = result.rows

        # And show them on the page
        return render_template("pages/home.jinja", teams=teams)


#-----------------------------------------------------------
# Team page route - Show details of a single team
#-----------------------------------------------------------
@app.get("/team/<code>")
def show_team_details(code):
    with connect_db() as client:
        # Get the team details from the DB
        sql = "SELECT code, name, description, website FROM teams WHERE code=?"
        params = [code]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so keep going
            team = result.rows[0]

            # Get the team players from the DB
            sql = "SELECT name, notes FROM players WHERE team=?"
            params = [code]
            result = client.execute(sql, params)
            players = result.rows

            return render_template("pages/team.jinja", team=team, players=players)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a team, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def add_a_team():
    # Get the data from the form
    code        = request.form.get("code")
    name        = request.form.get("name")
    description = request.form.get("description")
    website     = request.form.get("website")

    # Sanitise the text inputs
    name = html.escape(name)
    description = html.escape(description)

    # Get the uploaded image
    image_file = request.files['image']
    if not image_file:
        return server_error("Problem uploading image")

    # Load the image data ready for the DB
    image_data = image_file.read()
    mime_type = image_file.mimetype

    with connect_db() as client:
        # Add the team to the DB
        sql = """
            INSERT INTO teams (code, name, description, website, image_data, image_mime)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = [code, name, description, website, image_data, mime_type]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Team '{name}' added", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for adding a team, using data posted from a form
#-----------------------------------------------------------
@app.post("/add-player")
def add_a_player():
    # Get the data from the form
    team  = request.form.get("team")
    name  = request.form.get("name")
    notes = request.form.get("notes")

    # Sanitise the text inputs
    name  = html.escape(name)
    notes = html.escape(notes)

    with connect_db() as client:
        # Add the player to the DB
        sql = """
            INSERT INTO players (name, notes, team)
            VALUES (?, ?, ?)
        """
        params = [name, notes, team]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Player '{name}' added", "success")
        return redirect(f"/team/{team}")


#-----------------------------------------------------------
# Route for deleting a team, code given in the route
#-----------------------------------------------------------
@app.get("/delete/<code>")
def delete_a_thing(code):
    with connect_db() as client:
        # Delete the team from the DB
        sql = "DELETE FROM teams WHERE code=?"
        params = [code]
        client.execute(sql, params)

        # Go back to the home page
        flash("Team deleted", "success")
        return redirect("/things")


#-----------------------------------------------------------
# Route for serving an image from DB for a given team
#-----------------------------------------------------------
@app.route('/image/<code>')
def get_image(code):
    with connect_db() as client:
        sql = "SELECT image_data, image_mime FROM teams WHERE code = ?"
        params = [code]
        result = client.execute(sql, params)

        return image_file(result, "image_data", "image_mime")

