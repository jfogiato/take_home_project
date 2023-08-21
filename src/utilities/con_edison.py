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

            date_parts = date_string.split(" ")

            if len(date_parts[-1]) == 2:
                format_string = "%b %d, %y"
            else:
                format_string = "%b %d, %Y"

            return datetime.strptime(date_string, format_string).strftime("%Y-%m-%d")
        
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

        # Search for delivery charge using regex + a capturing group, extract the group, and convert to cents
        delivery_charge = re.search(r"Total electricity delivery charges (\$[1-9]\d{0,2}(?:,\d{3})*(?:\.\d{2})?)", full_pdf_text)

        if delivery_charge is None:
            delivery_charge = None
        else:
            delivery_charge = convert_to_cents(delivery_charge.group(1))

        # Search for supply charge using regex + a capturing group, extract the group, and convert to cents
        supply_charge = re.search(r"Total electricity supply charges (\$[1-9]\d{0,2}(?:,\d{3})*(?:\.\d{2})?)", full_pdf_text)

        if supply_charge is None:
            supply_charge = None
        else:
            supply_charge = convert_to_cents(supply_charge.group(1))

        # Search for community solar bill credit using regex + a capturing group, extract the group, and convert to cents
        community_solar_bill_credit = re.search(r"ADJUSTMENT INFORMATION.*?\$([\d.]+)", full_pdf_text, re.DOTALL)

        if community_solar_bill_credit is None:
            community_solar_bill_credit = None
        else:
            community_solar_bill_credit = convert_to_cents(community_solar_bill_credit.group(1))


        # METERS

         # Determine if it's a uni/multi meter bill
        single_meter_raw = re.search(r"(\d{9}) (\d+) (Actual|Estimate) (\w{3} \d{1,2}, \d{2}) (\d+) (Actual|Estimate|Start) (\w{3} \d{1,2}, \d{2}) (\d+) ?(\d+) (\d+) kWh", full_pdf_text)

        multi_meter_raw = re.findall(r"([A-Z]) ([A-Z]) (\d{9}) (\d+) (Estimated|Actual) (\d+) (Estimated|Actual) (\d+) (\d+) (\d+)", full_pdf_text)

        meters = []

        # Execute logic based on whether it's a single or multi meter bill or neither
        if single_meter_raw is None and len(multi_meter_raw) == 0 and delivery_charge is None:
            meters = []

        elif single_meter_raw is not None:

            tariff = re.search(r"Rate: ([A-Z][A-Z]\d{1,2}.*)", full_pdf_text).group(1)

            meter = {}
            meter["id"] = single_meter_raw.group(1)
            meter["type"] = 'electric' if tariff[:2] == 'EL' else None
            meter["billing_period_from"] = convert_to_iso_date(single_meter_raw.group(7))
            meter["billing_period_to"] = convert_to_iso_date(single_meter_raw.group(4))
            meter["consumption"] = convert_to_watts(single_meter_raw.group(10))
            meter["tariff"] = tariff
            meters.append(meter)

        elif len(multi_meter_raw) != 0:

            tariff = re.search(r"Rate: ([A-Z][A-Z]\d{1,2}.*)", full_pdf_text).group(1)

            for meter in multi_meter_raw:
                new_meter = {}
                new_meter["id"] = meter[2]
                new_meter["type"] = 'electric' if tariff[:2] == 'EL' else None
                new_meter["billing_period_from"] = billing_period_from
                new_meter["billing_period_to"] = billing_period_to
                new_meter["consumption"] = convert_to_watts(meter[9])
                new_meter["tariff"] = tariff
                meters.append(new_meter)


        # Search for electricity consumption using regex + a capturing group, extract the group, and convert to wH
        # ** NEED TO TIE THIS DIRECTLY TO METERS LIST **
        electricity_consumption = 0

        if len(meters) == 0:
            electricity_consumption = None
        else:
            for meter in meters:
                electricity_consumption += meter["consumption"]

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
            "meters": meters
        }