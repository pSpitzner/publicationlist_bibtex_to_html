# ------------------------------------------------------------------------------ #
# @Author:        F. Paul Spitzner
# @Email:         paul.spitzner@ds.mpg.de
# @Created:       2021-02-08 14:06:35
# @Last Modified: 2021-02-11 22:13:43
# ------------------------------------------------------------------------------ #
# pip install pylatexenc, bibtexparser
#
# Simple script to generate a html list of publications from an existing
# bibtex file, or to create one from scatch.
#
# I needed to cleanup my abstracts in zotero a bit. When fetching metadata
# automatically, sometimes the introduction can get copied into bibtex fields.
# ------------------------------------------------------------------------------ #

import bibtexparser
from bibtexparser.bparser import BibTexParser
import bibtexparser.customization as btxc

from pylatexenc.latex2text import LatexNodes2Text


# ------------------------------------------------------------------------------ #
# Settings
# ------------------------------------------------------------------------------ #

bibtex_path = "/path/to/zotero_libarary.bib"
output_path = "/path/to/targe_file.html"

# whether to include abstracts. this part is still a bit hacky, so disable if dislike.
show_abstracts = True

# this gets placed before/after the main publist that is created in main()
page_prefix = """
<!doctype html>
<html lang="en">
<head>
<title>My Publications</title>
</head>

<body>
<div class="row">
<div id="content-publications" class="content animate col-12 pt-lg-2">

<h2 class="d-inline d-sm-none">Publications</h2>
"""

page_suffix = """
</div>
</div>
</body>
"""


def main():
    global db, entries
    with open(bibtex_path) as bibtex_file:
        parser = BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        db = bibtexparser.load(bibtex_file, parser=parser)
    print(f"Found {len(db.entries)} entries in '{bibtex_path}'")

    # put these into the order in which they should appear online. customize below
    cite_keys = [
        "contreras_towards_2020",
        "contreras_challenges_2021",
        "spitzner_mr_2020",
        "dehning_inferring_2020",
        "neto_unified_2020",
        "spitzner_droplet_2018",
        "zierenberg_percolation_2017",
        "fricke_scaling_2017",
    ]

    entries = dict()
    for key in cite_keys:
        entries[key] = get_entry_for_citekey(db, key)

    # ------------------------------------------------------------------------------ #
    # customize entries
    # ------------------------------------------------------------------------------ #

    # badges should be a list of dicts, where each dict has 'name' and 'url'

    entries["contreras_challenges_2021"]["badges"] = [
        {"name": "arXiv", "url": "https://arxiv.org/abs/2009.05732"},
    ]


    entries["contreras_towards_2020"]["badges"] = [
        {"name": "arXiv", "url": "https://arxiv.org/abs/2011.11413"},
    ]
    entries["contreras_towards_2020"]["year"] = "submitted"
    entries["contreras_towards_2020"]["journal"] = ""


    entries["spitzner_mr_2020"]["badges"] = [
        {"name": "GitHub", "url": "https://github.com/Priesemann-Group/mrestimator"},
        {"name": "arXiv", "url": "https://arxiv.org/abs/2007.03367"},
    ]
    entries["spitzner_mr_2020"]["year"] = "under review"
    entries["spitzner_mr_2020"]["journal"] = ""


    entries["dehning_inferring_2020"]["badges"] = [
        {"name": "GitHub", "url": "https://github.com/Priesemann-Group/covid19_inference_forecast"},
        {"name": "arXiv", "url": "https://arxiv.org/abs/2004.01105"},
    ]

    entries["neto_unified_2020"]["badges"] = [
        {"name": "GitHub", "url": "https://github.com/Priesemann-Group/criticalavalanches"},
        {"name": "arXiv", "url": "https://arxiv.org/abs/1910.09984"},
    ]
    entries["neto_unified_2020"]["year"] = "under review"
    entries["neto_unified_2020"]["journal"] = ""


    entries["zierenberg_percolation_2017"]["badges"] = [
        {"name": "arXiv", "url": "https://arxiv.org/abs/1708.02296"},
    ]


    entries["fricke_scaling_2017"]["badges"] = [
        {"name": "arXiv", "url": "https://arxiv.org/abs/1703.10368 "},
    ]

    # ------------------------------------------------------------------------------ #
    # or built custom entries from scratch. nested dict.
    # missing fields wont be printed
    # ------------------------------------------------------------------------------ #

    other = {
        "msc_spitzner": {
            "author": "Spitzner, Franz Paul",
            "title": "Two Perspectives on the Condensation-Evaporation Transition of the Lennard-Jones Gas in 2D",
            "journal": "Master Thesis, Leipzig University",
            "url": "https://www.physik.uni-leipzig.de/~spitzner/publications/2017-spitzner-two_perspectives_on_the_condensation-evaporation_transition_of_the_lennard-jones_gas_in_2d.pdf",
        },
        "hauptseminar": {
            "author": "Spitzner, Franz Paul",
            "title": "Der Münchhausen-Trick — Pulling oneself up by one’s bootstrap",
            "journal": "Hauptseminar, Leipzig University",
            "url": "https://www.physik.uni-leipzig.de/~spitzner/publications/Spitzner_bootstrap.pdf",
        },
        "bsc_spitzner": {
            "author": "Spitzner, Franz Paul",
            "title": "Generating Long-range Power-law Correlated Disorder",
            "journal": "Bachelor Thesis, Leipzig University",
            "url": "https://www.physik.uni-leipzig.de/~spitzner/publications/Spitzner_CorrelatedDisorder.pdf",
        },
    }

    # ------------------------------------------------------------------------------ #
    # build html source code
    # ------------------------------------------------------------------------------ #

    html = ""
    html += page_prefix

    html += "<h3>Journal Articles</h3>"
    # it's nice to have things in a list so they get rendered well when css fails
    html += '<ul class="pub_list">\n'
    for key in cite_keys:
        html += entry_to_html(entries[key])
    html += "</ul>\n\n"

    html += "<h3>Other</h3>"
    html += '<ul class="pub_list">\n'
    for key in other.keys():
        html += entry_to_html(other[key])
    html += "</ul>\n\n"

    html += page_suffix

    # ------------------------------------------------------------------------------ #
    # write to file
    # ------------------------------------------------------------------------------ #
    if output_path is not None and len(output_path) > 0:
        with open(output_path, "w") as text_file:
            text_file.write(html)
        print(f"Output written to {output_path}")
    else:
        print("No ouput_path set, not writing any output. Edit this script!")


# fmt:off
def entry_to_html(entry):
    """
        Converts the entry dict for every publication into formatted html.
        Customize as needed to change the style of every list item.
    """
    html = ""

    # make it a list item
    html += "<li>\n"

    # format authors
    if 'author' in entry and len(entry['author']) > 0:
        html += '<div class="pub_author">\n'
        html += format_authors(entry)
        # html += ':'
        html += "\n</div>\n"

    # format titles as links that lead to the url
    if 'title' in entry and len(entry['title']) > 0:
        html += '<a class="pub_title"\n'
        if 'url' in entry and len(entry['url']) > 0:
            html += 'href="' + entry['url'] + '"\n'
        html += '>\n'
        # title
        html += cleanup(entry['title'])
        # html += ','
        html += '\n</a>\n'

    # I wanted journal, year and badges in one line -> spans enclosed in one div
    html += '<div class="pub_journal_group">\n'

    # journal, volume, pages
    if 'journal' in entry and len(entry['journal']) > 0:
        html += '<span class="pub_journal">\n'
        html += entry['journal']
        if 'volume' in entry and len(entry['volume']) > 0:
            html += ' ' + entry['volume']
        if 'pages' in entry and len(entry['pages']) > 0:
            html += ', ' + entry['pages']
        html += '\n</span>\n'

    # year
    if 'year' in entry and len(entry['year']) > 0:
        html += '<span class="pub_year">\n'
        html += '(' + entry['year'] + ')'
        html += '\n</span>\n'

    # size-dependent newline before the badges, this uses bootstrap classes
    html += '<br class="d-block d-lg-none">'

    # abstract badge first (toggles whether the abstract is displayed or not)
    if show_abstracts and 'abstract' in entry and len(entry['abstract']) > 0:
        html += '<span class="pub_badge">\n'
        html += '['
        html += '<span class="fake_a pub_badge_link" '
        html += 'data-toggle="collapse" aria-expanded="false" '
        html += 'data-target="#abstract_' + entry['ID'] + '">'
        html += "Abstract"
        html += '</span>'
        html += ']\n'
        html += '</span>\n'


    # badges for arxiv and the likes
    if 'badges' in entry and len(entry['badges']) > 0:
        for b in entry['badges']:
            assert 'url' in b and 'name' in b
            html += '<span class="pub_badge">\n'
            html += '['
            html += '<a class="pub_badge_link"'
            html += 'href="' + b['url'] + '">'
            html += b['name']
            html += '</a>'
            html += ']'
            html += '\n</span>\n'

    html += '</div>\n' # journal group

    # abstract div
    if show_abstracts and 'abstract' in entry and len(entry['abstract']) > 0:
        html += '<div class="collapse" id="abstract_' + entry['ID'] + '">\n'
        html += '<div class="pub_abstract">'
        html += cleanup(entry['abstract'])
        html += '</div>\n'
        html += '</div>'

    html += '</li>\n\n' # list item

    return html
# fmt:on


# ------------------------------------------------------------------------------ #
# helper functions
# ------------------------------------------------------------------------------ #


def cleanup(raw):
    """
        helper to clean up text that comes from bibtex and does not work well
        in html.
    """
    res = LatexNodes2Text().latex_to_text(raw)
    # res = res.replace("<p>", "")
    # res = res.replace("</p>", "")
    # I use double quotes for attributes. hence, only use single quotes in text
    res = res.replace('"', "'")
    # escape quotes, see https://pagedart.com/blog/single-quote-in-html/
    # res = res.replace('"', '&#34;')
    # res = res.replace("'", '&#39;')
    # res = res.replace('&', '&amp;')
    # res = res.replace('<', '&lt;')
    # res = res.replace('>', '&gt;')
    return res


# %%
def get_entry_for_citekey(db, key):
    """
        db : bibtex database
        key : string, the citekey to look for
    """
    for e in db.entries:
        if "ID" in e and e["ID"] == key:
            return e


def get_entries_for_author(db, author_strings):
    """
        could be combined with bibtexparser combinations. for now, not assumed!
        (think of checking against the full string that is in the .bib file as author)

        db : bibtex database
        author_strings : list of strings to search for in the authors field
    """
    res = []
    for e in db.entries:
        if "author" not in e:
            continue
        for s in author_strings:
            if s.lower() in e["author"].lower():
                res.append(e)
                break
    return res


# %%
def format_authors(entry, abbreviate_first=True, et_al_at=1000):
    """
        this is the way i like it, tweak as needed.
    """

    # Split author field into a list of “Name, Surname”. seems to be inplace,
    # thats why we copy first
    r = entry.copy()
    btxc.author(r)
    names = r["author"]
    authors = []

    for name in names:
        # {'first': ['F.', 'Paul'], 'last': ['Spitzner'], 'von': [], 'jr': []}
        split = btxc.splitname(name)
        # print(split)
        if not abbreviate_first:
            first = " ".join(split["first"])
        else:
            first = ""
            for f in split["first"]:
                # name spelled out
                if len(f) > 2:
                    first += f[0] + "."
                elif f[1] in ".:;":
                    first += f[0] + "."
                else:
                    print(
                        f"Adapt the `format_authors` script to your needs for entry {r['ID']}"
                    )

        last = " ".join(split["last"])
        von = " ".join(split["von"])
        jr = " ".join(split["jr"])

        # stitch the name together and fix capitalziation
        temp = first.title()
        if len(von) > 0:
            temp += " " + von.lower()
        temp += " " + last  # do not title case this, breaks e.g. "de Heuvel"
        if len(jr) > 0:
            temp += " " + jr.lower()

        authors.append(temp)

    res = ""
    # now we have a list of authors nicely formatted, make this a readable
    # one-liner for the webiste
    if len(authors) > et_al_at:
        res = authors[0] + " et al."
    elif len(authors) == 1:
        res = authors[0]
    else:
        res = authors[0]
        for a in authors[1:-1]:
            res += ", " + a
        res += " and " + authors[-1]

    # cleanup bibtex brackets
    res = cleanup(res)
    # res = res.replace("{", "")
    # res = res.replace("}", "")
    return res


if __name__ == "__main__":
    main()
