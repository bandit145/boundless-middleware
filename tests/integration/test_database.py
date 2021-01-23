from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import boundless.mainway_objects as objs
import datetime
import logging
import os
import atexit

##cleanup garbage
def delete_db():
    os.remove("boundless_test.sqlite")


if not os.getenv("CLEANUP"):
    atexit.register(delete_db)
####


def define_db():
    engine = create_engine("sqlite:///boundless_test.sqlite")
    objs.Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def clear_table(session, name):
    session.execute("delete from {}".format(name))
    session.commit()


def test_poi_create():
    discordid = 100057952664162304
    session = define_db()
    session.add(objs.Poi(discordid=discordid))
    session.commit()
    data = session.execute(
        "select * from pois where discordid=:discordid", {"discordid": discordid}
    ).fetchall()
    assert data[0][1] == discordid
    logging.info(data[0])
    clear_table(session, "pois")


def test_mainway_report():
    discordid = 100057952664162304
    session = define_db()
    poi = objs.Poi(
        discordid=discordid, pos_comments=100, neg_comments=50, flagged_comments=150
    )
    location = objs.Location(type="discord", name="test server", pois=[poi])
    session.add_all([poi, location])
    session.commit()
    incidents = [
        objs.Incident(
            writeup="bad thing",
            type="kick",
            poi=poi.id,
            location=location.id,
            date=datetime.datetime.now(),
        ),
        objs.Incident(
            writeup="bad thing2",
            type="kick",
            poi=poi.id,
            location=location.id,
            date=datetime.datetime.now(),
        ),
    ]
    session.add_all(incidents)
    session.commit()
    # logging.info(report)
    # assert type(report) == str
