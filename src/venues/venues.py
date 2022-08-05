from flask import Blueprint, render_template

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

from app import *


venues = Blueprint("venues", __name__,
                   static_folder="/static", template_folder="/templates")


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
