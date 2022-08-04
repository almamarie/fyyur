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
    "seeking_talent": artist.seeking_talent,
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
