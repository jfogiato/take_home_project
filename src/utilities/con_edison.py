from pypdf import PdfReader
import re
from datetime import datetime

class ConEdison:
    
    def parse_bill(file):

        # Helpers 🤝
        def convert_to_cents(dollar_amount):
            # Ran into a weird issue involving floating point numbers and the conversion to cents
            # Had to split on the decimal and convert each part to an int
            dollars, cents = dollar_amount.replace(",", "").replace("$", "").split('.')
            converted_dollars = int(dollars) * 100
            converted_cents = int(cents) if converted_dollars > 0 else int(cents) * -1

            return converted_dollars + converted_cents
        
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
        outstanding_balance = re.search(r"Total charges from your last bill (-?\$[1-9]\d{0,2}(?:,\d{3})*(?:\.\d{2})?)", full_pdf_text)

        if outstanding_balance is None:
            outstanding_balance = 0
        else :
            outstanding_balance = convert_to_cents(outstanding_balance.group(1))


        # Search for full billing period from using regex + two capturing groups, extract each group, and convert to datetime object
        full_billing_period = re.search(r"Billing period: (\w{3} \d{1,2}, \d{4})  to (\w{3} \d{1,2}, \d{4})", full_pdf_text)

        if full_billing_period is None:
            billing_period_from = None
            billing_period_to = None
        else: 
            billing_period_from = convert_to_iso_date(full_billing_period.group(1))
            billing_period_to = convert_to_iso_date(full_billing_period.group(2))


        # Search for total amount due using regex + a capturing group, extract the group, and convert to cents
        # I guessed on format of the potential amount due here becuase the PDF I was working with didn't have an amount due - will revisit
        total_amount = re.search(r"Total amount due (\$[1-9]\d{0,2}(?:,\d{3})*(?:\.\d{2})?)", full_pdf_text)

        if total_amount is None:
            total_amount = 0
        else :
            total_amount = convert_to_cents(total_amount.group(1))

        # Search for electricity consumption using regex + a capturing group, extract the group, and convert to wH
        # ** NEED TO DIE THIS DIRECTLY TO METERS LIST **
        # electricity_consumption = convert_to_watts(re.search(r"Delivery (\d+) kWh", full_pdf_text).group(1))

        # Search for delivery charge using regex + a capturing group, extract the group, and convert to cents
        # delivery_charge = re.search(r"Total electricity delivery charges \$([\d.]+)", full_pdf_text)

        # if delivery_charge is None:
        #     delivery_charge = None
        # else:
        #     delivery_charge = convert_to_cents(delivery_charge.group(1))

        # Search for supply charge using regex + a capturing group, extract the group, and convert to cents
        # supply_charge = re.search(r"Total electricity supply charges \$([\d.]+)", full_pdf_text)

        # if supply_charge is None:
        #     supply_charge = None
        # else:
        #     supply_charge = convert_to_cents(supply_charge.group(1))

        # Search for community solar bill credit using regex + a capturing group, extract the group, and convert to cents
        # community_solar_bill_credit = convert_to_cents(re.search(r"Adjustments -\$(\d+\.\d{2})", full_pdf_text).group(1))

        
        # meter_string = r"(\d{9}) (\d{4}) (Estimated|Actual) (\w{3} \d{1,2}, \d{2}) (\d{4}) (Estimated|Actual) (\w{3} \d{1,2}, \d{2}) (\d+) (\d+) kWh"

        # meters_list_raw = re.findall(meter_string, full_pdf_text)

        # meters = []

        # for meter in meters_list_raw:
        #     meter = {}
        #     meter["id"] = meter[0]
        #     meter["type"] = 'Electric' # Placeholder
        #     meter["billing_period_from"] = convert_to_iso_date(meter[6])
        #     meter["billing_period_to"] = convert_to_iso_date(meter[3])
        #     meter["consumption"] = convert_to_watts(meter[8])
        #     meter["tariff"] = "EL1 Residential or Religious" # Placeholder
        #     meters.append(meter)


        return {
            "account_number": account_number,
            "billed_on": billed_on,
            "outstanding_balance": outstanding_balance,
            "billing_period_from": billing_period_from,
            "billing_period_to": billing_period_to,
            "total_amount": total_amount,
            # "electricity_consumption": electricity_consumption,
            # "delivery_charge": delivery_charge,
            # "supply_charge": supply_charge,
            # "community_solar_bill_credit": community_solar_bill_credit,
            # "meters": []
        }