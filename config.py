# ProQuest base url
base_url = "https://ebookcentral.proquest.com"
# name of your institution (mentioned in URL of books for e.g.)
# https://ebookcentral.proquest.com/lib/XYZ/detail.action?docID=4568785&query=%22Incident+Management%22%2C
# change to the correct one
institution = "XYZ"
# Use keyring or manual login
use_keyring = True
# Enter ProQuest username
username = ""
# leave empty if using keyring
password = ""

# default citing style, overwritten by --style, -s parameter
default_style = "Test"
# dict with citing styles, put placeholders in dollar signs
# see a list of available placeholders at the end of this file
styles = {
    "APA6": "",
    "Test": "$Erscheinungs- termin Print$, \"$Titel$\" von $Autor$"
}

# list of available placeholders
# - $Titel$
# - $Autor$
# - $Verlag$
# - $Erscheinungs- termin Print$
# - $Erscheinungs- termin E-book$
# - $Sprache$
# - $Druck ISBN$
# - $E-Book ISBN$
# - $Seiten$
# - $LC-Schlagwort$
# - $LC Call Number$
# - $Dewey-Dezimalnummer$
# - $BISAC Subject Headings$
# - $Dokumenttyp$