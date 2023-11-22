# stufi-sim
Calculate your (student) loan for different scenarios.

## Installation
The project is build using:
- Python
- [Poetry](https://python-poetry.org/)
- Jupyter notebook (One option is to use it within VSCode (https://code.visualstudio.com/docs/datascience/jupyter-notebooks))

Once you have these tools installed, open a terminal and setup the project using:
```sh
poetry install
```

Alternatively, you can use a regular python script instead of a jupyter notebook. 

## Usage

The `LoanScenario` class will simulate a single scenario. Set it up by passing variables to the constructor. Then call `.calculate()` to simulate for this scenario.

Multiple instances of this class can be created to simulate multiple scenarios.

See `stufi-sim.ipynb` for an example.

## Parameters
`LoanScenario` takes the following parameters:
- L0: Start Loan (L) amount
- B0: Start (combined) Balance (B) (overall balance on on your bank accounts)
- start_year: First year to include in the simulation.
- end_year: Last year to include in the simulation.
- LC_dict:  This is a dictionary mapping dates (first day of each month) to Change of the Loan (LC) in this month: how much you are adding/repaying per month.
- BC_dict: This is a dictionary mapping dates (first day of each month) to the Monthly Balance Change (BC) (Income-Expenses).
- R_dict: This is a dictionary mapping dates (first day of each month) to the Yearly interest Rate (R) (in %).

The dictionaries mapping dates do not have to contain every month. They can for example contain only the first date. All dates after it will then automatically be filled with the same number. 
