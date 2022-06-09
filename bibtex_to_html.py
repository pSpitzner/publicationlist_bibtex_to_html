# ------------------------------------------------------------------------------ #
# @Author:        F. Paul Spitzner
# @Email:         paul.spitzner@ds.mpg.de
# @Created:       2021-02-08 14:06:35
# @Last Modified: 2022-06-09 15:46:19
# ------------------------------------------------------------------------------ #
# pip install pylatexenc bibtexparser
#
# Simple script to generate a html list of publications from an existing
# bibtex file, or to create one from scatch.
#
# I needed to cleanup my abstracts in zotero a bit. When fetching metadata
# automatically, sometimes the introduction can get copied into bibtex fields.
#
# clean latex parsing for abstracts is still not there 100%
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

# whether to show the altmetric badge, this requires extra javascript on your page:
# <script type='text/javascript' src='https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js'></script>
# see https://api.altmetric.com/embeds.html
# to get arxiv ids automatically, see readme
show_altmetric = True

show_arxiv_badge = True

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
        # do not skip non-standard bibtex fields
        parser.ignore_nonstandard_types = False
        db = bibtexparser.load(bibtex_file, parser=parser)
    print(f"Found {len(db.entries)} entries in '{bibtex_path}'")

    # put these into the order in which they should appear online. customize below
    cite_keys = [
        "yamamoto_modular_2022",
        "hagemann_intrinsic_2022",
        "contreras_low_2021",
        "leite_-synuclein_2022",
        "contreras_challenges_2021",
        "spitzner_mr_2021",
        "dehning_inferring_2020",
        "neto_unified_2020",
        "spitzner_droplet_2018",
        "zierenberg_percolation_2017",
        "fricke_scaling_2017",
    ]

    print(f"Fetching selected {len(cite_keys)} entries")
    entries = get_entry_for_citekey(db, cite_keys)

    # ------------------------------------------------------------------------------ #
    # customize entries
    # ------------------------------------------------------------------------------ #

    # preprints, remove year
    entries["hagemann_intrinsic_2022"]["year"] = "submitted"
    entries["hagemann_intrinsic_2022"]["journal"] = ""

    entries["yamamoto_modular_2022"]["year"] = "submitted"
    entries["yamamoto_modular_2022"]["journal"] = ""

    # badges should be a list of dicts, where each dict has 'name' and 'url'
    entries["spitzner_mr_2021"]["badges"] = [
        {"name": "GitHub", "url": "https://github.com/Priesemann-Group/mrestimator"},
    ]


    entries["dehning_inferring_2020"]["badges"] = [
        {"name": "GitHub", "url": "https://github.com/Priesemann-Group/covid19_inference_forecast"},
    ]

    entries["neto_unified_2020"]["badges"] = [
        {"name": "GitHub", "url": "https://github.com/Priesemann-Group/criticalavalanches"},
    ]
    entries["neto_unified_2020"]["year"] = "under review"
    entries["neto_unified_2020"]["journal"] = ""

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
    print(f"Building html")

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

    # year, only show this if we have a journal and not a preprint
    if 'year' in entry and len(entry['year']) > 0:
        html += '<span class="pub_year">\n'
        html += '(' + entry['year'] + ')'
        html += '\n</span>\n'

    # size-dependent newline before the badges, this uses bootstrap classes
    # html += '<br class="d-block d-lg-none">'
    html += '<br class="d-block d-lg-block">'

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
    def format_badge(name, url):
        badge = '<span class="pub_badge">\n'
        badge += '['
        badge += '<a class="pub_badge_link"'
        badge += 'href="' + url + '">'
        badge += name
        badge += '</a>'
        badge += ']'
        badge += '\n</span>\n'
        return badge

    if 'badges' in entry and len(entry['badges']) > 0:
        for b in entry['badges']:
            assert 'url' in b and 'name' in b
            html += format_badge(b['name'], b['url'])

    # arxiv badge
    if show_arxiv_badge and "arxiv_org_id" in entry:
        html += format_badge("arXiv", "https://arxiv.org/abs/" + entry["arxiv_org_id"])

    # altmetric badge
    if show_altmetric and ("arxiv_org_id" in entry or "doi" in entry):
        html += '<span data-badge-type="2" '
        html += 'data-hide-no-mentions="true" '
        html += 'class="altmetric-embed" '
        # I prefer arxiv id over doi
        if "arxiv_org_id" in entry:
            html += f'data-arxiv-id="{entry["arxiv_org_id"]}"'
        else:
            html += f'data-doi="{entry["doi"]}"'
        html += ' ></span>\n'

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
    # bibtex escapes stuff, which breaks parsing

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


def get_entry_for_citekey(db, key):
    """
        db : bibtex database
        key : string, the citekey to look for, or list of strings
    """

    if isinstance(key, list):
        keys = key
    else:
        keys = [key]

    entries = dict()
    for e in db.entries:
        if "ID" in e and e["ID"] in keys:
           entries[e["ID"]] = e

    for e in entries.values():
        find_arxiv_id_in_entry(e, add_to_entry=True)

    if len(entries) == 1:
        return list(entries.values())[0]
    return entries



def find_arxiv_id_in_entry(entry, add_to_entry = True):
    """
        There are a bunch of different places where an arxiv.org id may be hidden in
        the bibtex or biblatex files. Lets try some common places, and if we find it
        set it as a custom key.

        Adds (overwrites) `arxiv_org_id` if it can be found
        and `add_to_entry` is True (default)
    """

    arxiv_id = None
    while arxiv_id is None:
        if "eprint" in entry.keys() and "eprinttype" in entry.keys():
            # this is the default from BetterBibTex
            if entry["eprinttype"].lower() == "arxiv":
                arxiv_id = entry["eprint"]
                break

        if "doi" in entry.keys():
            # as of 2022 arxiv preprints get DOIs as `arXiv.2201.NNNNN`
            if "arXiv." in entry["doi"]:
                arxiv_id = entry["doi"].split("arXiv.", 1)[1]

        if "url" in entry.keys() and "arxiv.org/abs/" in entry["url"]:
            # avoid bioarxiv
            # https://www.biorxiv.org/content/early/2018/04/11/299859
            arxiv_id = entry["url"].split("arxiv.org/abs/", 1)[1]
            break
        break

    if add_to_entry and arxiv_id is not None:
        entry["arxiv_org_id"] = arxiv_id

    return arxiv_id





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
