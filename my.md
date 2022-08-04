# Useful resources

Filtering queries with multiple values e.g

[link here] (https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_filter_operators.htm#:~:text=nath%40gmail.com-,AND,customers.id%20%3E%20%3F%20OR%20customers.name%20LIKE%20%3F,-The%20output%20for)

    `...WHERE id=2 AND/OR name='Louis Marie Atoluko Ayariga'`

## Implementing Search

like() method itself produces the LIKE criteria for WHERE clause in the SELECT expression.

```
    result = session.query(Customers).filter(Customers.name.like('Ra%'))
    for row in result:
    print("ID:", row.id,"Name: ",row.name,"Address:",row.address,"Email:",row.email)
```

using `ilike` makes the comparation case insensitive.

use
`Artist.query.with_entities(Artist.id, Artist.name).all()`
`
to fetch some columns

and
`artistDetails = Artist.query.with_entities( Artist.name, Artist.image_link).filter(Artist.id == pastShow.artist_id).first()`

to fetch some columns with a filter
