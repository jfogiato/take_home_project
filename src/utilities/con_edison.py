from pypdf import PdfReader
import re
from datetime import datetime

class ConEdison:

    def convert_to_cents(dollar_amount):
        dollars, cents = dollar_amount.replace(",", "").replace("$", "").split('.')
        multiplier = 1 if int(dollars) > 0 else -1

        converted_dollars = int(dollars) * 100

        if len(cents) == 2:
            converted_cents = int(cents)
        elif len(cents) == 1:
            converted_cents = int(cents) * 10
        else:
            converted_cents = int(cents) * .1

        return converted_dollars + (converted_cents * multiplier)
    
    def convert_to_iso_date(date_string):

        date_parts = date_string.split(" ")

        if len(date_parts[-1]) == 2:
            format_string = "%b %d, %y"
        else:
            format_string = "%b %d, %Y"

        return datetime.strptime(date_string, format_string).strftime("%Y-%m-%d")
        
    def convert_to_watts(kwh):
        return int(float(kwh) * 1000)
    
    def parse_bill(file, self):
        
        # Read PDF file and extract text
        reader = PdfReader(file)

        full_pdf_text = ""

        for page in reader.pages:
            full_pdf_text += page.extract_text() + "\n"
        
        # Search for account number using regex + a capturing group, extract the group, and remove dashes
        account_number_regex = r"(\d{2}-\d{4}-\d{4}-\d{4}-\d{1})"
        account_number = re.search(fr"Account number: {account_number_regex}", full_pdf_text).group(1).replace("-", "")

        # Search for billed on date using regex + a capturing group, extract the group, and convert to datetime object
        date_4_digit_year_regex = r"(\w{3} \d{1,2}, \d{4})"
        billed_on = self.convert_to_iso_date(re.search(fr"Your billing summary as of {date_4_digit_year_regex}", full_pdf_text).group(1))

        # Search for outstanding balance using regex + a capturing group, handle conditionally
        floating_point_currency_regex = r"(-?\$[0-9,\.]*)"
        outstanding_balance_match = re.search(fr"Balance from previous bill {floating_point_currency_regex}", full_pdf_text)

        if outstanding_balance_match is None:
            outstanding_balance = 0
        else :
            outstanding_balance = self.convert_to_cents(outstanding_balance_match.group(1))

        # Search for full billing period using regex + two capturing groups, handle conditionally
        full_billing_period_match = re.search(fr"Billing period: {date_4_digit_year_regex}  to {date_4_digit_year_regex}", full_pdf_text)

        if full_billing_period_match is None:
            billing_period_from = None
            billing_period_to = None
        else: 
            billing_period_from = self.convert_to_iso_date(full_billing_period_match.group(1))
            billing_period_to = self.convert_to_iso_date(full_billing_period_match.group(2))

        # Search for total amount due using regex + a capturing group, handle conditionally
        total_amount_match = re.search(fr"Total amount due {floating_point_currency_regex}", full_pdf_text)

        if total_amount_match is None:
            total_amount = 0
        else:
            total_amount = self.convert_to_cents(total_amount_match.group(1))

        # Search for delivery charge using regex + a capturing group, handle conditionally
        delivery_charge_match = re.search(fr"Total electricity delivery charges {floating_point_currency_regex}", full_pdf_text)

        if delivery_charge_match is not None:
            delivery_charge = self.convert_to_cents(delivery_charge_match.group(1))
        else:
            delivery_charge = None

        # Search for supply charge using regex + a capturing group, handle conditionally
        supply_charge_match = re.search(fr"Total electricity supply charges {floating_point_currency_regex}", full_pdf_text)

        if supply_charge_match is not None:
            supply_charge = self.convert_to_cents(supply_charge_match.group(1))
        else:
            supply_charge = None

        # Search for community solar bill credit using regex + a capturing group, handle conditionally
        community_solar_regex = r"ADJUSTMENT INFORMATION.*?\$([\d.]+).*\n.*\n.*community.*project\."
        community_solar_bill_credit_match = re.search(community_solar_regex, full_pdf_text, re.DOTALL)

        if community_solar_bill_credit_match is not None:
            community_solar_bill_credit = self.convert_to_cents(community_solar_bill_credit_match.group(1))
        else:
            community_solar_bill_credit = None

        # Search for meters & tarrif using regex
        single_meter_regex = r"(\d{9}) (\d+) (Actual|Estimate) (\w{3} \d{1,2}, \d{2}) (\d+) (Actual|Estimate|Start) (\w{3} \d{1,2}, \d{2}) (\d+) ?(\d+) (\d+) kWh"
        multi_meter_regex = r"([A-Z]) ([A-Z]) (\d{9}) (\d+) (Estimated|Actual) (\d+) (Estimated|Actual) (\d+) (\d+) (\d+)"
        tarriff_regex = r"Rate: ([A-Z][A-Z]\d{1,2}.*)"
        single_meter_raw_match = re.search(single_meter_regex, full_pdf_text)
        multi_meter_raw_match = re.findall(multi_meter_regex, full_pdf_text)
        tariff_match = re.search(tarriff_regex, full_pdf_text)
        
        # Declare meters and tariff variable, if there is a match, extract the group, otherwise, set to None
        tariff = tariff_match.group(1) if tariff_match is not None else None
        meters = []

        # If there is a single meter, create a meter object and append it to the meters list
        if single_meter_raw_match is not None:
            meter = {}
            meter["id"] = single_meter_raw_match.group(1)
            meter["type"] = 'electric' if tariff[:2] == 'EL' else None
            meter["billing_period_from"] = self.convert_to_iso_date(single_meter_raw_match.group(7))
            meter["billing_period_to"] = self.convert_to_iso_date(single_meter_raw_match.group(4))
            meter["consumption"] = self.convert_to_watts(single_meter_raw_match.group(10))
            meter["tariff"] = tariff
            meters = [meter]

        # Iterate over the multi meter matches, create a meter object for each, and append it to the meters list
        # If there are no multi meter matches, meters will be an empty list
        for meter in multi_meter_raw_match:
            new_meter = {}
            new_meter["id"] = meter[2]
            new_meter["type"] = 'electric' if tariff[:2] == 'EL' else None
            new_meter["billing_period_from"] = billing_period_from
            new_meter["billing_period_to"] = billing_period_to
            new_meter["consumption"] = self.convert_to_watts(meter[9])
            new_meter["tariff"] = tariff
            meters.append(new_meter)

        # If there are no meters, consumption is None, otherwise, loop through the meters and add up the consumption
        if len(meters) == 0:
            electricity_consumption = None
        else:
            electricity_consumption = 0
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