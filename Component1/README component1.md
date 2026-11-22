# Component 1 -- Community Bakery Simulation
This project simulates a bakry business process with orders, sales, purchases over a chosen number of weeks.

## Development history

Stage 1 repairs and regression tests were committed to the main branch
and tagged as `stage1-complete`.

Stage 2 development continued on a separate branch from the tagged
commit. Additional docstrings and PEP 8 formatting improvements were
made to the Stage 1 test files during Stage 2 without moving the
original tag.

## Running the tests

Interactive mode

python3 main.py

<Stage 1>
python3 -m unittest discover -s tests -v

JSON replay mode

python3 main.py --scenario data/example.json --decisions data/example_decisions.json --output output/run.json

<Stage 2>
python3 -m unittest discover -s tests_stage2 -v

JSON replay mode

python3 main.py --scenario data/example_order.json --decisions data/example_decisions.json --output output/run.json


## Files

- main.py – Interactive interface and command-line entry point
- bakery.py – Weekly simulation, cash, labour and order processing
- stock.py – Inventory and weekly ingredient losses
- product.py – Product definitions and recipes
- ingredient.py – Ingredient definitions
- recipeitem.py – Relationship between ingredients and recipes
- validation.py – Input validation
- replay.py – JSON loading and scenario replay
- order.py – Individual advance order and status
- orderbook.py – Order validation, storage and selection of due orders
