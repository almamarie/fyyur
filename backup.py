#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from collections import defaultdict
import enum
from hashlib import new
import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import or_
from forms import *
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# class enumGenres(enum.Enum):
#     Alternative = enum.auto()
#     Blues = enum.auto()
#     Classical = enum.auto()
#     Country = enum.auto()
#     Electronic = enum.auto()
#     Folk = enum.auto()
#     Funk = enum.auto()
#     Hip-Hop = enum.auto()
#     Heavy Metal = enum.auto()
#     Instrumental = enum.auto()
#     Jazz = enum.auto()
#     'Musical Theatre' = enum.auto()
#     Pop = enum.auto()
#     Punk = enum.auto()
#     R & B = enum.auto()
#     Reggae = enum.auto()
#     Rock n Roll = enum.auto()
#     Soul = enum.auto()
#     Other = enum.auto()


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    def __repr__(self):
        return f'<Venue {self.id} {self.city}  {self.state}>'

    # my tables
    genres = db.Column(db.String())
    website_link = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())

    artists = db.relationship(
        'Artist', secondary='show', backref=db.backref('artist', lazy=True))


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # my tables
    website_link = db.Column(db.String())
    seeking_venue = db.Column(db.String())
    seeking_description = db.Column(db.String())


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    allQueries = Venue.query.all()
    # all = Venue.query.distinct(Venue.city, Venue.state).all()

    response = createResponseObject(groupQuery(allQueries))
    # print('distinct   ', createResponseObject(all))
    return render_template('pages/venues.html', areas=response)


def groupQuery(venuesList):
    groups = defaultdict(list)

    for venue in venuesList:
        groups[venue.city, venue.state].append(venue)

    return groups.values()


def createResponseObject(groupedQuery):
    response = []
    for group in groupedQuery:
        obj = {
            "city": "",
            "state": "",
            "venues": []
        }
        obj['city'] = group[0].city
        obj['state'] = group[0].state

        # print(obj)
        for g in group:
            data = {
                "id": 0,
                "name": "",
                "num_upcoming_shows": 0,
            }
            data['id'] = g.id
            data['name'] = g.name
            # current_time = datetime.datetime.utcnow()
            data["num_upcoming_shows"] = getNumberOfupcomingShows(g.id)

            obj["venues"].append(data)

        response.append(obj)
        # print(obj)

    return response

# This helper function generates a list of objects containing id, name and number of upcoming shows


def generatenumberUpcomingShowsList(queryList):
    generatedList = []
    for g in queryList:
        data = {
            "id": 0,
            "name": "",
            "num_upcoming_shows": 0,
        }
        data['id'] = g.id
        data['name'] = g.name
        # current_time = datetime.datetime.utcnow()
        data["num_upcoming_shows"] = getNumberOfupcomingShows(
            g.id) or data["num_upcoming_shows"]

        generatedList.append(data)
    return generatedList


# Helper function used to get number of upcoming shows.
def getNumberOfupcomingShows(id):
    return Show.query.filter(
        Show.venue_id == id).filter(Show.start_time > datetime.now()).count()

# Helper function used to get number of past shows.


def getNumberOfPastShows(id):
    return Show.query.filter(
        Show.venue_id == id).filter(Show.start_time < datetime.now()).count()


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    search_term = request.form.get('search_term')
    print('search_term ', search_term)
    # allMatchingShows = Venue.query.filter(
    #     or_(Venue.name.like(search_term + "%"), Venue.name.like(search_term.lower() + "%"))).all()
    allMatchingShows = Venue.query.filter(
        Venue.name.ilike("%" + search_term + "%")).all()
    # print(allMatchingShows)
    response['data'] = generatenumberUpcomingShowsList(allMatchingShows)
    response['count'] = len(response['data'])
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    template = {
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "genres": ["Classical", "R&B", "Hip-Hop"],
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0,
    }

    # fetch the details of the venue with the id specified
    venue = Venue.query.filter(Venue.id == venue_id).first()
    # if not venue:
    #     flash(
    #         'An error occurred. Venue ' + request.form['name'] + ' was not found.')
    #     return

    template = {
        "id": venue_id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link,
    }
    print("venue: ", venue)

    # fetch all the past shows of the venue from the shows table
    listOfPastShows = getListOfPastShows("venue", venue_id)

    print("list of past shows", listOfPastShows)
    # update number of past shows
    template["past_shows_count"] = len(listOfPastShows)

    # for each show fetch the id (already gotten), name, and image of the artist performing in the show
    template["past_shows"] = parseShows("venue", listOfPastShows)

    # fetch all the upcoming shows of the venue
    listOfUpcomingShows = getListOfUpcomingShows("venue", venue_id)

    # update number of upcoming shows
    template["upcoming_shows_count"] = len(listOfUpcomingShows)

    # for each show fetch the id (already gotten), name, and image of the artist performing in the show
    template["upcoming_shows"] = parseShows("venue", listOfUpcomingShows)

    print('pastShows done: ', template)
    return render_template('pages/show_venue.html', venue=template)


def parseShows(database, queryList):
    parsed = []
    print("parsing a list of ", len(queryList), " shows")
    if database == "artist":
        for pastShow in queryList:
            print("pastshow", pastShow.id)
            venueDetails = Artist.query.with_entities(
                Artist.name, Artist.image_link).filter(Artist.id == pastShow.artist_id).first()
            print(venueDetails)
            tmp = {
                "venue_id": pastShow.id,
                "venue_name": venueDetails.name,
                "venue_image_link": venueDetails.image_link,
                "start_time": str(pastShow.start_time)

            }

            print("tmp: ", tmp)
            parsed.append(tmp)
    elif database == "venue":
        for pastShow in queryList:
            print("pastshow", pastShow.id)
            artistDetails = Artist.query.with_entities(
                Artist.name, Artist.image_link).filter(Artist.id == pastShow.artist_id).first()
            print(artistDetails)
            tmp = {
                "artist_id": pastShow.id,
                "artist_name": artistDetails.name,
                "artist_image_link": artistDetails.image_link,
                "start_time": str(pastShow.start_time)

            }

            print("tmp: ", tmp)
            parsed.append(tmp)
    return parsed


def getListOfPastShows(database, id):
    if database == "venue":
        return Show.query.filter(
            Show.venue_id == id).filter(Show.start_time < datetime.now()).all()
    elif database == "artist":
        return Show.query.filter(
            Show.artist_id == id).filter(Show.start_time < datetime.now()).all()


def getListOfUpcomingShows(database, id):
    if database == "venue":
        return Show.query.filter(
            Show.venue_id == id).filter(Show.start_time > datetime.now()).all()
    elif database == "artist":
        return Show.query.filter(
            Show.artist_id == id).filter(Show.start_time > datetime.now()).all()

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    is_Successful = False
    try:
        new_Venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            facebook_link=request.form['facebook_link'],
            image_link=request.form['image_link'],
            website_link=request.form['website_link'],
            seeking_description=request.form["seeking_description"]
        )
        try:
            if (request.form['seeking_talent']):
                new_Venue.seeking_talent = True
        except:
            new_Venue.seeking_talent = False

        print("G    enres: ", request.form.getlist('genres'))
        db.session.add(new_Venue)
        db.session.commit()
        is_Successful = True
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # on successful db insert, flash success

    flash('Venue ' + request.form['name'] + ' was successfully listed!') if is_Successful else flash(
        'An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    is_Successful = False
    venue_name = ""
    try:
        venue = Venue.query.filter(Venue.id == venue_id).delete()
        db.session.commit()
        is_Successful = True
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # Note: The bonus challenge has to wait, there is no time and my Django is bad
    flash('Venue was successfully deleted!') if is_Successful else flash(
        'An error occurred. Venue could not be deleted.')

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that

    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.with_entities(Artist.id, Artist.name).all()
    # data=[{
    #   "id": 4,
    #   "name": "Guns N Petals",
    # }, {
    #   "id": 5,
    #   "name": "Matt Quevedo",
    # }, {
    #   "id": 6,
    #   "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }

    search_term = request.form.get('search_term')
    print('search_term ', search_term)
    # allMatchingShows = Venue.query.filter(
    #     or_(Venue.name.like(search_term + "%"), Venue.name.like(search_term.lower() + "%"))).all()
    allMatchingArtists = Artist.query.filter(
        Artist.name.ilike("%" + search_term + "%")).all()
    # print(allMatchingShows)
    response['data'] = generatenumberUpcomingShowsList(allMatchingArtists)
    response['count'] = len(response['data'])

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    # shows the artist page with the given artist_id

    # fetch the details of the artist with the id specified
    artist = Artist.query.filter(Artist.id == artist_id).first()
    # if not artist:
    #     flash(
    #         'An error occurred. artist ' + request.form['name'] + ' was not found.')
    #     return

    template = {
        "id": artist_id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": artist.seeking_venue,
        "image_link": artist.image_link,
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0,
    }
    print("artist: ", artist)

    # fetch all the past shows of the artist from the shows table
    listOfPastShows = getListOfPastShows("artist", artist_id)

    print("list of past shows", listOfPastShows)
    # update number of past shows
    template["past_shows_count"] = len(listOfPastShows)

    # for each show fetch the id (already gotten), name, and image of the artist performing in the show
    template["past_shows"] = parseShows("artist", listOfPastShows)

    # fetch all the upcoming shows of the artist
    listOfUpcomingShows = getListOfUpcomingShows("artist", artist_id)

    # update number of upcoming shows
    template["upcoming_shows_count"] = len(listOfUpcomingShows)

    # for each show fetch the id (already gotten), name, and image of the artist performing in the show
    template["upcoming_shows"] = parseShows("artist", listOfUpcomingShows)

    print('pastShows done: ', template)
    return render_template('pages/show_artist.html', artist=template)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.filter(Artist.id == artist_id).first()
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # artist record with ID <artist_id> using the new attributes
    is_Successful = False
    try:
        artist = Artist.query.filter(Artist.id == artist_id).one()

        artist.name = request.form['name'],
        artist.city = request.form['city'],
        artist.state = request.form['state'],
        artist.phone = request.form['phone'],
        artist.genres = request.form.getlist('genres'),
        artist.facebook_link = request.form['facebook_link'],
        artist.image_link = request.form['image_link'],
        artist.website_link = request.form['website_link'],
        artist.seeking_description = request.form["seeking_description"]

        if request.form.get("seeking_venue") == None:
            artist.seeking_venue = False
        else:
            artist.seeking_venue = True
        # try:
        #     artist.seeking_venue = True if request.form["seeking_venue"] else False
        # except:
        #     artist.seeking_venue = False

        print("I was here")
        db.session.add(artist)
        db.session.commit()
        is_Successful = True
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    flash('Artist details updated') if is_Successful else flash(
        'Error: Artist details not updated')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.filter(Venue.id == venue_id).first()
    form = VenueForm(obj=venue)
    print("Form: ", form)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    # venue record with ID <venue_id> using the new attributes
    is_Successful = False
    try:
        venue = Venue.query.filter(Venue.id == venue_id).one()

        # The genres only returns 1 value
        print("Genre: ", request.form.getlist("genres"))
        venue.name = request.form['name'],
        venue.city = request.form['city'],
        venue.state = request.form['state'],
        venue.address = request.form['address'],
        venue.phone = request.form['phone'],
        venue.genres = str(request.form.getlist('genres')),
        venue.facebook_link = request.form['facebook_link'],
        venue.image_link = request.form['image_link'],
        venue.website_link = request.form['website_link'],
        venue.seeking_description = request.form["seeking_description"]

        if request.form.get("seeking_talent") == None:
            venue.seeking_talent = False
        else:
            venue.seeking_talent = True

        db.session.add(venue)
        db.session.commit()
        is_Successful = True
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    flash('Venue details updated') if is_Successful else flash(
        'Error: Venue details not updated')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    is_Successful = False
    try:
        new_Artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            facebook_link=request.form['facebook_link'],
            image_link=request.form['image_link'],
            website_link=request.form['website_link'],
            seeking_description=request.form["seeking_description"]
        )
        try:
            if (request.form['seeking_talent'] == 'y'):
                new_Artist.seeking_venue = True
        except:
            new_Artist.seeking_venue = False
            print("Artist seeking Venue  ", Artist.seeking_venue)
        db.session.add(new_Artist)
        db.session.commit()
        is_Successful = True
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    flash('Artist ' + request.form['name'] + ' was successfully listed!') if is_Successful else flash(
        'An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows

    response = []
    allShows = Show.query.all()
    # print("All Shows", allShows)

    for show in allShows:
        artist = Artist.query.with_entities(
            Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).first()
        venue = Venue.query.with_entities(Venue.name).filter(
            Venue.id == show.venue_id).first()
        tmp = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        }
        response.append(tmp)
    return render_template('pages/shows.html', shows=response)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form

    is_successful = True

    try:
        # print('Date   ', format_datetime(request.form['start_time']))
        newShow = Show(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time'])
        db.session.add(newShow)
        db.session.commit()

    except:
        db.session.rollback()
        print(sys.exc_info())
        is_successful = False
    finally:
        db.session.close()

    # on successful db insert, flash success
    if is_successful:
        flash('Show was successfully listed!')
    else:
        flash('An error occurred. Show could not be listed.')
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
