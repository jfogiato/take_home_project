# Bayou At-Home Coding Challenge

Welcome to the Bayou at-home coding challenge! In this challenge, your task is to write a Python class for the Con Edison utility that passes the existing tests and fulfills the requirements outlined below.

## Getting Started

1. Clone this repository to your local machine using the following command:
    ```sh
    git clone git@github.com:Bayou-Energy/at_home_project.git
2. There's no default dependencies to install! Of course, you're free to use libraries and to create a `requirements.txt` file to keep track of your project dependencies.

3. Navigate to the project directory and run the test suite.
    ```sh
    cd at_home_project/src
    python tests.py

## Requirements

In this challenge, you are tasked with implementing the `parse_bill` function within the `ConEdison` class. This function should be designed to parse PDF bills from the folder `bill_pdfs/con_edison` and extract relevant information. The parsed information should be returned in a structured format as described below:

### Input

- `file`: An opened PDF file for the bill that needs to be parsed.

### Output

The `parse_bill` function should return a dictionary containing the extracted information. The dictionary should have the following keys:

- `account_number`: A string representing the account number for the bill.
- `billed_on`: A string representing the date the bill was generated (ISO8601 format).
- `outstanding_balance`: An integer representing the outstanding balance in cents.
- `billing_period_from`: A string representing the start date of the billing period (ISO8601 format).
- `billing_period_to`: A string representing the end date of the billing period (ISO8601 format).
- `total_amount`: An integer representing the total bill amount in cents.
- `electricity_consumption`: An integer representing the electricity consumption in watts.
- `delivery_charge`: An integer representing the delivery charge in cents.
- `supply_charge`: An integer representing the supply charge in cents.
- `community_solar_bill_credit`: An integer representing the bill credit related to community solar in cents.
- `meters`: A list of dictionaries, where each dictionary represents a meter. Each meter should have the following keys:
    - `id`: A unique identifier for the meter.
        type: A string representing the type of the meter.
    - `billing_period_from`: A string representing the start date of the meter's billing period (ISO8601 format).
    - `billing_period_to`: A string representing the end date of the meter's billing period (ISO8601 format).
    - `consumption`: An integer representing the consumption of the meter.
    - `tariff`: A string representing the tariff associated with the meter.

### Notes

- Money amounts should be converted to cents (multiply by 100) to ensure consistent representation.
- Dates should be in ISO8601 format (e.g., "2023-08-15").
- You can use any suitable libraries or tools to achieve the parsing task.
- You are encouraged to write additional helper functions or classes if they enhance the readability and organization of your code.
- Keep your code readable and maintainable, using meaningful variable names and comments to explain complex sections.
Your solution will be evaluated based on correctness, code quality, and efficiency.
- Feel free to reach out to us if you have any questions or need clarifications. We're here to help!

## Submission

Once you've written code that passes all the tests and fulfills the requirements, you're ready to submit your solution:
1. [Create a repository](https://github.com/new) on Github.
    - Choose `No template`
    - **Make it private**
    - Do not add a Readme, a .gitignore or a license
2. On your local machine, set your new project URL as the origin and push your code (don't forget to commit your last changes before pushing).
    ```sh
    git remote set-url origin git@github.com:<your_name>/<your_project_name>.git
    git push origin main
3. Give access to `joris.vanhecke@gmail.com` to your Github project. We'll be notified by Github and will review your project as soon as possible.

Good luck, and happy coding!