# TengenToppaAnimango

New version of the [aniMango](https://github.com/WarwickAnimeSoc/aniMango) site for the University of Warwick Anime and Manga Society.

This is the code that runs [animesoc.co.uk](https://animesoc.co.uk).

Built on Django and Bootstrap using a large amount of code from the old site.

## Running the Project

To run the site locally for development,
setup a virtual environment running Python 3.14,
and run `pip install -e .` to install the necessary dependencies.

In addition, you need:
- the config file, which future webmaster needs to copy from the production server (CHANGE CONFIG MODE TO DEBUG!)
- a local test MySQL server with the same format structure as the production server

The repository contains all other files needed to run the site.

To build bootstrap with the overwrites used by the site, you will need to copy the bootstrap source files into 
`.\static_files\scss` and use `sass` from `dart-sass` to build `ttam-bootstrap.scss`.

## Todo

- Styling and CSS need to be tweaked to look like more than just a generic bootstrap site.
