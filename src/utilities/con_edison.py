from pypdf import PdfReader
import re
from datetime import datetime

class ConEdison:
    
    def parse_bill(file):

        # Helpers 🤝
        def convert_to_cents(dollar_amount):
            # Checking for "None" here - keep or move to a conditional for the total_amount?
            if dollar_amount == "None":
                return 0
            # Ran into a weird issue involving floating point numbers and the conversion to cents
            # Had to split on the decimal and convert each part to an int
            dollars, cents = dollar_amount.split('.')
            return int(dollars) * 100 + int(cents)
        
        def convert_to_iso_date(date_string):
            return datetime.strptime(date_string, "%b %d, %Y").strftime("%Y-%m-%d")
        
        def convert_to_watts(kwh):
            return int(float(kwh) * 1000)
        
        # Create a PdfReader object from the file
        reader = PdfReader(file)
        # Parse every page of the PDF into a single string & assign to text variable with new lines
        full_pdf_text = ""
        for page in reader.pages:
            full_pdf_text += page.extract_text() + "\n"
        
        # Search for account number using regex + a capturing group, extract the group, and remove dashes
        account_number = re.search(r"Account number:\s+(\d{2}-\d{4}-\d{4}-\d{4}-\d{1})", full_pdf_text).group(1).replace("-", "")

        # Search for billed on date using regex + a capturing group, extract the group, and convert to datetime object
        billed_on = convert_to_iso_date(re.search(r"Your billing summary as of (\w{3} \d{1,2}, \d{4})", full_pdf_text).group(1))

        # Search for outstanding balance using regex + a capturing group, extract the group, and convert to cents
        outstanding_balance = convert_to_cents(re.search(r"Total charges from your last bill \$(\d+\.\d{2})", full_pdf_text).group(1))

        # Search for full billing period from using regex + two capturing groups, extract each group, and convert to datetime object
        full_billing_period = re.search(r"Billing period: (\w{3} \d{1,2}, \d{4})  to (\w{3} \d{1,2}, \d{4})", full_pdf_text)
        billing_period_from = convert_to_iso_date(full_billing_period.group(1))
        billing_period_to = convert_to_iso_date(full_billing_period.group(2))

        # Search for total amount due using regex + a capturing group, extract the group, and convert to cents
        # I guessed on format of the potential amount due here becuase the PDF I was working with didn't have an amount due - will revisit
        total_amount = convert_to_cents(re.search(r"Total amount due (None|\$\d+\.\d{2})", full_pdf_text).group(1))

        # Search for electricity consumption using regex + a capturing group, extract the group, and convert to wH
        electricity_consumption = convert_to_watts(re.search(r"Delivery (\d+) kWh", full_pdf_text).group(1))

        # Search for delivery charge using regex + a capturing group, extract the group, and convert to cents
        delivery_charge = convert_to_cents(re.search(r"Total electricity delivery charges \$([\d.]+)", full_pdf_text).group(1))

        # Search for supply charge using regex + a capturing group, extract the group, and convert to cents
        supply_charge = convert_to_cents(re.search(r"Total electricity supply charges \$([\d.]+)", full_pdf_text).group(1))

        # Search for community solar bill credit using regex + a capturing group, extract the group, and convert to cents
        # Don't love this because adjstments could contain other things, but struggled to implement it another way
        community_solar_bill_credit = convert_to_cents(re.search(r"Adjustments -\$(\d+\.\d{2})", full_pdf_text).group(1))

        # print(full_pdf_text)

        meters = []

        # Need to figure out a way to loop based on number of lines found
        for i in range (0, 1):
            # Meter # New Reading Reading Type Date Prior Reading Reading Type Date Reading Diff Total Usage
            #  (000000000) 9603 Actual (Sep 13, 22) 9067 Actual (Aug 12, 22) 536 (536 kWh)
            meter_info = re.search(r"(\d{9}) (\d{4}) (Estimated|Actual) (\w{3} \d{1,2}, \d{4}) (\d{4}) (Estimated|Actual) (\w{3} \d{1,2}, \d{4}) (\d+) (\d+) kWh", full_pdf_text)
            print('meter info: ', meter_info.group(1))

            # meter = {}
            # meter["id"] = 
            # meter["type"] = 
            # meter["billing_period_from"] = 
            # meter["billing_period_to"] = 
            # meter["consumption"] = 
            # meter["tariff"] = 
            # meters.append(meter)

        return {
            "account_number": account_number,
            "billed_on": billed_on,
            "outstanding_balance": outstanding_balance,
            "billing_period_from": billing_period_from,
            "billing_period_to": billing_period_to,
            "total_amount": total_amount,
            "electricity_consumption": electricity_consumption,
            "delivery_charge": delivery_charge,
            "supply_charge": supply_charge,
            "community_solar_bill_credit": community_solar_bill_credit,
            "meters": []
        }