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

artists = Blueprint("artists", __name__,
                    static_folder="/static", template_folder="/templates")


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
