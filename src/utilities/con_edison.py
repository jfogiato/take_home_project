class ConEdison:
    
    def parse_bill(file):

        return {
            "account_number": "000000000000000",
            "billed_on": "2022-03-14",
            "outstanding_balance": 6341768,
            "billing_period_from": "2022-02-02",
            "billing_period_to": "2022-03-04",
            "total_amount": 7677567,
            "electricity_consumption": 127200000,
            "delivery_charge": 1335799,
            "supply_charge": None,
            "community_solar_bill_credit": None,
            "meters": [
                {
                    'id': '000000000', 
                    'type': 'electric', 
                    'billing_period_from': '2022-02-02', 
                    'billing_period_to': '2022-03-04', 
                    'consumption': 60800000, 
                    'tariff': 'EL9 General Large'
                },
                {
                    'id': '000000000',
                    'type': 'electric',
                    'billing_period_from':'2022-02-02',
                    'billing_period_to': '2022-03-04',
                    'consumption': 66400000,
                    'tariff': 'EL9 General Large'
                }
            ]
        }