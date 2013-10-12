# -*- coding: UTF-8 -*-
import sys
from urllib2 import quote
from xlrd import open_workbook
from rdflib import *
from rdflib.extras.describer import Describer


def quote_utf8(v):
    return quote(v.encode('utf-8'))

def parse_date(v):
    if v is None or v == u"":
        return v
    if isinstance(v, unicode):
        if v[0] == '[':
            v = v[1:-1]
        else:
            v = v.split()[0]
    else:
        v = u"%i" % v
    dt = XSD.date if '-' in v else XSD.gYear
    return Literal(v, datatype=dt)

def if_value(d, p, v, **kws):
    if v is None or v == u"":
        return
    d.value(p, v, **kws)


DCT = Namespace("http://purl.org/dc/terms/")
PROV = Namespace("http://www.w3.org/ns/prov#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DBP = Namespace("http://dbpedia.org/ontology/")
STV = Namespace("http://diska.kb.se/skillingtryck/vocab#")

graph = Graph()
for k, o in vars().items():
    if isinstance(o, Namespace):
        graph.bind(k.lower(), o)

lang = 'sv'

d = Describer(graph, base="http://diska.kb.se/skillingtryck/")

book = open_workbook(sys.argv[1])

# Works Sheet
works_sheet = book.sheet_by_index(0)
for i in range(1, works_sheet.nrows):
    row = works_sheet.row_values(i)
    num = u"%i" % row[0] if isinstance(row[0], float) else row[0]
    d.about("work/%s" % num)
    d.rdftype(DCT.BibliographicResource)
    with d.rev(FOAF.primaryTopic, "work/%s/record" % num):
        d.rdftype(FOAF.Document)
        if_value(d, RDFS.label, num) # Löpnr katalogkort
        if_value(d, RDFS.comment, row[8], lang=lang) # Anmärkning
    if_value(d, DCT.title, row[1], lang=lang) # Term / Händelse, titel, tryck / kort
    if_value(d, DCT.description, row[2], lang=lang) # Term / Händelse beskrivning
    if any(row[3:6]):
        with d.rel(DCT.creator):
            d.rdftype(FOAF.Person)
            # Person / Författare, efternamn
            if_value(d, FOAF.surname, row[3])
            # Person / Författare, förnamn
            if_value(d, FOAF.firstName, row[4])
            # Person / Författare, alternativa namn, endast initialer
            if_value(d, FOAF.nick, row[5])
    with d.rel(PROV.wasGeneratedBy):
        d.rdftype(PROV.Activity)
        if_value(d, PROV.endedAtTime, parse_date(row[6])) # Tryckår
        if row[7]: # Tryckort
            with d.rel(PROV.atLocation, "place/%s" % quote_utf8(row[7])):
                d.rdftype(DBP.PopulatedPlace)
                d.value(RDFS.label, row[7])

# Persons Sheet
persons_sheet = book.sheet_by_index(1)
for i in range(1, persons_sheet.nrows):
    row = persons_sheet.row_values(i)
    # TODO: use birth and death to further avoid conflation
    person_id = "person/%s_%s" % (quote_utf8(row[1]), quote_utf8(row[0]))
    d.about(person_id)
    d.rdftype(FOAF.Person)
    if_value(d, FOAF.surname, row[0]) # Person / Efternamn
    if_value(d, FOAF.firstName, row[1]) # Person / Förnamn
    if_value(d, FOAF.nick, row[2]) # Person / Alternativa namn
    if_value(d, DBP.birthDate, parse_date(row[3])) # Person/ Födelseår / datum
    # Person / Födelseår / datum # enligt källa Andersson, Hans "Aldrig kommer duvungar blå utav korpäggen vita: Skillingtryck om brott och straff 1708-1937" Uppsala 2006.
    if_value(d, STV.birthDate_alt_duvungar, parse_date(row[4]))
    # Person / Dödsår / datum
    if_value(d, DBP.deathDate, parse_date(row[5]))
    # Person / Dödsår / datum # enligt Andersson, Hans ...
    if_value(d, STV.deathDate_alt_duvingar, parse_date(row[6]))
    # Person / Dödsår / datum enligt källa Andersson, Hans "Från dygdiga Dorotea till bildsköne Bengtsson: berättelser om brott i Sverige under 400 år" u.o. 2009.
    if_value(d, STV.deathYearOrDate_alt_dorotea, parse_date(row[7]))
    if_value(d, FOAF.title, row[8], lang=lang) # Person / Yrke, titel
    # Förekommer / anknytning till händelse i visa (löpnr katalogkort)
    with d.rev(PROV.agent):
        if_value(d, PROV.hadRole, row[9].strip(), lang=lang) # Person / Roll i trycket
        # TODO: can event be disambiguated in source data?
        event_markers = [quote_utf8(parse_date(v)[0] if isinstance(v, float) else v)
                         for v in row[10:18] if v]
        event_id = "event/%s" % ",".join(event_markers)
        refs = [num.replace(' ', '') for num in
                ("%i" % row[18] if isinstance(row[18], float)
                    else row[18]).split(",")]
        if not row[10] and len(event_markers) < 5:
            event_id += ";%s" % ",".join(refs)
        with d.rev(PROV.qualifiedAssociation, event_id):
            d.rdftype(PROV.Activity)
            if_value(d, RDFS.label, row[10], lang=lang) # Term / Händelse, namn
            # Händelse / datum, första tidpunkt
            if_value(d, PROV.startedAtTime, parse_date(row[11]))
            # Händelse / datum, sista tidpunkt
            if_value(d, PROV.endedAtTime, parse_date(row[12]))
            # Händelse / händelstyp
            if_value(d, DCT.type, row[13], lang=lang)
            if any(row[14:18]):
                # TODO: reference locations in DBPedia if possible
                def describe_region():
                    if_value(d, DBP.region, row[16]) # Plats / Händelseplats, landskap
                    if_value(d, DBP.country, row[17]) # Plats / Händelseplats, land
                def link_city(rel):
                    city_id = "place/%s" % quote_utf8(row[15])
                    with d.rel(rel, city_id):
                        d.rdftype(DBP.PopulatedPlace)
                        d.value(RDFS.label, row[15])
                        describe_region()
                if row[14]: # Plats / Händelseplats, adress
                    loc_id = BNode("place-" +
                            "-".join(quote_utf8(v) for v in row[14:18] if v)
                            .replace("%", "0"))
                    with d.rel(PROV.atLocation, loc_id):
                        d.value(RDFS.label, row[14])
                        if row[15]: # Plats / Händelseplats, ort
                            link_city(DBP.city)
                        else:
                            describe_region()
                elif row[15]:
                    link_city(PROV.atLocation)
                else:
                    with d.rel(PROV.atLocation):
                        describe_region()
            for num in refs:
                d.rev(FOAF.primaryTopic, "work/%s" % num)
            if_value(d, RDFS.comment, row[19]) # Anmärkning

graph.serialize(sys.stdout, format='turtle')
