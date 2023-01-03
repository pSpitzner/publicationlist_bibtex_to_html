# Create a html list of your publications
based on an existing bibtex library.

```
pip install pylatexenc, bibtexparser
```


One thing I am trying to do is work with arxiv.org ids to fetch altmetrics and create a
badge automatically. This is a bit of a thing and afaik there is no uniform _right way_ how to get it consistent across zotero, bibtex, biblatex and csl.

My recommendation, for now:
* use the [BetterBibtex plugin for zotero](https://retorque.re/zotero-better-bibtex/)
* make sure that in the extra field you have the arxiv id in the format `arXiv:2007.03367`
* BBT will pick this up and populate the `eprint` and `eprinttype` fields in the exported `.bib`
