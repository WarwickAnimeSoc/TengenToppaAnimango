# TengenToppaAnimango

New version of the [aniMango](https://github.com/WarwickAnimeSoc/aniMango) site for the University of Warwick Anime and Manga Society.

This is the code that runs [animesoc.co.uk](https://animesoc.co.uk).

Built on Django and Bootstrap using a large amount of code from the old site.

## Running the Project

To run the site locally for development, you should set up a virtual environment running Python 3.8.5 and install all
the necessary dependencies from `requirements.txt` . Additionally, you will need a MySQL server running in the same 
format as the one on the server.

This repository contains all the files needed to run the site, except for the config files, which future webmasters will
need to copy to their machine from the server.

To build bootstrap with the overwrites used by the site, you will need to copy the bootstrap source files into 
`.\static_files\scss` and use `pysassc` to build `ttam-bootstrap.scss`.

## Todo

- Styling and CSS need to be tweaked to look like more than just a generic bootstrap site.
- (For the live site) The history entries from the old site DB need to be copied over.