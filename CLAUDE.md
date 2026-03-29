# Claude

This project is a collection of short lessons on the design and
testing of research software.  Each lesson builds a toy version of a
real research application in Python.  In this context "toy version"
mean at most 200 lines of well-structured Python.  Applications may
include fluid flow simulation, astronomical or medical image analysis,
genetic sequence alignment, topic modeling, lexical diversity, or
anything else that would be done by a research software engineer.  The
aim is to cover a wide range of fields in a way that is accessible to
many learners rather than going into depth for a small number of
learners.

Each example is developed in small steps.  A step might change or undo
something done in a previous step in order to illustrate an
incremental, iterative design process.

Small Python scripts are created to generate synthetic data for use in
lessons and examples. These scripts are placed in the same directory
as the lesson. Their filenames start with `generate_`. All synthetic
data generators that use random number generation use 7493418 as the
RNG seed.

Tests to validate that the code implements the science correctly are
developed and explained in tandem with the application code.
Tolerances in tests (e.g., comparing floating point values within a
certain tolerance) are justified explicitly rather than being chosen
arbitrarily.  Different testing and validation techniques are shown.

## Audience

Learners are comfortable using the Unix shell, doing basic operations
with Git, writing functions and classes in Python, using Polars for
dataframe manipulation, and Vega-Altair for data visualization.
Learners have never written a conditional in a Unix shell script or a
decorator in Python (though they have used Python decorators).  They
have completed first-year calculus and statistics but may not remember
much beyond the basics.  Learners use an LLM as a coding assistant but
write and debug code themselves.

## Skills

-   Load the `learning-goal` and `learning-opportunities` skills when
    creating lessons.

## Structure

-   Lessons are written in Markdown and compiled to HTML using the `mccole` static site generator.
-   Boilerplate Markdown files:
    -   `CODE_OF_CONDUCT.md`
    -   `CONTRIBUTING.md`
    -   `LICENSE.md`
-   Lesson files:
    -   `README.md`: lesson home page (including table of contents used by `mccole`).
    -   `*/index.md`: lessons (see `README.md` for order).
    -   `docs`: generated HTML.
    -   `_extras/links.md`: Markdown link definitions included in all other Markdown files.
    -   `_static/`: web site assets.
    -   `_templates/`: `jinja2` page template.
-   Custom Python scripts are put in `bin/*.py`.
    -   This project has a `uv` virtual environment, so use `python` rather than `python3` to run commands.

## Build and Test Commands

-   Repeatable actions are saved in `Makefile`.
    -   Run `make` with no arguments to get an up-to-date list of targets.
-   `make site` rebuilds the website from the Markdown files.
-   `make html` checks the generated HTML (but is slow, so should only be used before `git commit`).
-   `make test` uses `pytest` to run all tests.
-   Use `pytest directory` to run the tests in a particular lesson directory during development.
-   When running Python programs that generate charts or images,
    be sure to run them in the lesson directory so that the output file is created in that directory.

## Style Rules

-   Lessons are written as point-form notes.
-   Each lesson should take about an hour to work through.
-   Do not use type annotations in Python code.
-   Do not use **bold** or *italics* in prose.
-   Figures, code inclusions, citations, and glossary references are formatted using `mccole` shortcodes.
-   Do not attempt to be funny or offer generic positive feedback to readers.
-   Use `[text][key]` format for external links, and define `key` in `_extras/links.md`.
-   Do not over-use semi-colons or em-dashes.
-   Format mathematics using KaTeX.

## Interaction

-   Save a summary of prompts given and actions taken in Markdown files in `./log`
    with the UTC date and time of the start of the session as the file name.
-   Run shell commands that do not modify files without asking for permission.

# Formative Assessments

Formative self-assessments are embedded in lesson pages and checked
entirely in the browser.  They target different levels of
understanding, from recall of definitions and procedural ordering to
quantitative reasoning and interpretation of results.

Assessments are positioned within sections (not at the end of the
lesson) to follow the Segmenting and Immediate Feedback Timing
principles from principles.md: learners check their understanding
before moving on to the next concept, not only after reading
everything.

Assessments are implemented using the `@gvwilson/forma` JavaScript
package, which provides:

- concept map
- flashcard
- labeling
- matching
- multiple choice
- numeric entry
- ordering
- predict-then-check

Each assessment is wrapped in a `<div>` with attributes required by
the forma package and `markdown="1"` so that content can be formatted
as Markdown rather than HTML.

## Glossary

The glossary is stored in `glossary/index.md` as a Markdown definition
list.  Each entry has the form:

    <span id="some-key">term being defined</span>
    :   definition

To reference a glossary term in a lesson, use the shortcode:

    [%g some-key "display text" %]

where `some-key` matches the `id` attribute of the glossary entry
and `display text` is the phrase as it appears in the lesson prose.
