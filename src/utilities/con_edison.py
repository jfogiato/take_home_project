from pypdf import PdfReader
import re
from datetime import datetime

class ConEdison:

    def convert_to_cents(dollar_amount):
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
    
    def parse_bill(file, self):
        
        # Read PDF file and extract text
        reader = PdfReader(file)

        full_pdf_text = ""

        for page in reader.pages:
            full_pdf_text += page.extract_text() + "\n"
        
        # Search for account number using regex + a capturing group, extract the group, and remove dashes
        account_number = re.search(r"Account number:\s+(\d{2}-\d{4}-\d{4}-\d{4}-\d{1})", full_pdf_text).group(1).replace("-", "")

        # Search for billed on date using regex + a capturing group, extract the group, and convert to datetime object
        billed_on = self.convert_to_iso_date(re.search(r"Your billing summary as of (\w{3} \d{1,2}, \d{4})", full_pdf_text).group(1))

        # Search for outstanding balance using regex + a capturing group, handle conditionally
        outstanding_balance = re.search(r"Total charges from your last bill (-?\$[1-9]\d{0,2}(?:,\d{3})*(?:\.\d{2})?)", full_pdf_text)

        if outstanding_balance is None:
            outstanding_balance = 0
        else :
            outstanding_balance = self.convert_to_cents(outstanding_balance.group(1))

        # Search for full billing period using regex + two capturing groups, handle conditionally
        full_billing_period = re.search(r"Billing period: (\w{3} \d{1,2}, \d{4})  to (\w{3} \d{1,2}, \d{4})", full_pdf_text)

        if full_billing_period is None:
            billing_period_from = None
            billing_period_to = None
        else: 
            billing_period_from = self.convert_to_iso_date(full_billing_period.group(1))
            billing_period_to = self.convert_to_iso_date(full_billing_period.group(2))


        # Search for total amount due using regex + a capturing group, handle conditionally
        total_amount = re.search(r"Total amount due (\$[1-9]\d{0,2}(?:,\d{3})*(?:\.\d{2})?)", full_pdf_text)

        if total_amount is None:
            total_amount = 0
        else:
            total_amount = self.convert_to_cents(total_amount.group(1))

        # Search for delivery charge using regex + a capturing group, handle conditionally
        delivery_charge = re.search(r"Total electricity delivery charges (\$[1-9]\d{0,2}(?:,\d{3})*(?:\.\d{2})?)", full_pdf_text)

        if delivery_charge is not None:
            delivery_charge = self.convert_to_cents(delivery_charge.group(1))
            

        # Search for supply charge using regex + a capturing group, handle conditionally
        supply_charge = re.search(r"Total electricity supply charges (\$[1-9]\d{0,2}(?:,\d{3})*(?:\.\d{2})?)", full_pdf_text)

        if supply_charge is not None:
            supply_charge = self.convert_to_cents(supply_charge.group(1))
            

        # Search for community solar bill credit using regex + a capturing group, handle conditionally
        community_solar_bill_credit = re.search(r"ADJUSTMENT INFORMATION.*?\$([\d.]+)", full_pdf_text, re.DOTALL)

        if community_solar_bill_credit is not None:
            community_solar_bill_credit = self.convert_to_cents(community_solar_bill_credit.group(1))

        # Meter(s) Logic
        # Determine if it's a uni/multi meter bill
        single_meter_raw = re.search(r"(\d{9}) (\d+) (Actual|Estimate) (\w{3} \d{1,2}, \d{2}) (\d+) (Actual|Estimate|Start) (\w{3} \d{1,2}, \d{2}) (\d+) ?(\d+) (\d+) kWh", full_pdf_text)
        multi_meter_raw = re.findall(r"([A-Z]) ([A-Z]) (\d{9}) (\d+) (Estimated|Actual) (\d+) (Estimated|Actual) (\d+) (\d+) (\d+)", full_pdf_text)
        meters = []

        if single_meter_raw is None and len(multi_meter_raw) == 0 and delivery_charge is None: # 
            meters = []

        elif single_meter_raw is not None:
            tariff = re.search(r"Rate: ([A-Z][A-Z]\d{1,2}.*)", full_pdf_text).group(1)

            meter = {}
            meter["id"] = single_meter_raw.group(1)
            meter["type"] = 'electric' if tariff[:2] == 'EL' else None
            meter["billing_period_from"] = self.convert_to_iso_date(single_meter_raw.group(7))
            meter["billing_period_to"] = self.convert_to_iso_date(single_meter_raw.group(4))
            meter["consumption"] = self.convert_to_watts(single_meter_raw.group(10))
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
                new_meter["consumption"] = self.convert_to_watts(meter[9])
                new_meter["tariff"] = tariff
                meters.append(new_meter)

        # If there are no meters, consumption is None, otherwise, loop through the meters and add up the consumption
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