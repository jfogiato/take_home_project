import unittest
from utilities.con_edison import ConEdison

class BillParsingTestCase(unittest.TestCase):

    def test_con_edison_with_uni_meter_with_credit(self):
        with open("../bill_pdfs/con_edison/uni_meter_with_credit.pdf", "rb") as bill:
            parsed_values = ConEdison.parse_bill(bill)
            self.assertEqual(parsed_values["account_number"], "000000000000000")
            self.assertEqual(parsed_values["billed_on"], "2022-09-14")
            self.assertEqual(parsed_values["outstanding_balance"], 16454)
            self.assertEqual(parsed_values["billing_period_from"], "2022-08-12")
            self.assertEqual(parsed_values["billing_period_to"], "2022-09-13")
            self.assertEqual(parsed_values["total_amount"], 0)
            # self.assertEqual(parsed_values["electricity_consumption"], 536000)
            self.assertEqual(parsed_values["delivery_charge"], 10147)
            self.assertEqual(parsed_values["supply_charge"], 6846)
            # self.assertEqual(parsed_values["community_solar_bill_credit"], 45452)
            # self.assertEqual(parsed_values["meters"], [{'id': '000000000', 'type': 'electric', 'billing_period_from': '2022-08-12', 'billing_period_to': '2022-09-13', 'consumption': 536000, 'tariff': 'EL1 Residential or Religious'}])
    
    # @unittest.skip("Skipping this test for now")
    def test_con_edison_with_multi_meter_complex_delivery_no_credits(self):
        with open("../bill_pdfs/con_edison/multi_meter_complex_delivery_no_credits.pdf", "rb") as bill:
            parsed_values = ConEdison.parse_bill(bill)
            self.assertEqual(parsed_values["account_number"], "000000000000000")
            self.assertEqual(parsed_values["billed_on"], "2022-03-14")
            self.assertEqual(parsed_values["outstanding_balance"], 6341768)
            self.assertEqual(parsed_values["billing_period_from"], "2022-02-02")
            self.assertEqual(parsed_values["billing_period_to"], "2022-03-04")
            self.assertEqual(parsed_values["total_amount"], 7677567)
            # self.assertEqual(parsed_values["electricity_consumption"], 127200000)
            self.assertEqual(parsed_values["delivery_charge"], 1335799)
            self.assertEqual(parsed_values["supply_charge"], None)
            # self.assertEqual(parsed_values["community_solar_bill_credit"], None)
            # self.assertEqual(parsed_values["meters"], [
            #     {'id': '000000000', 'type': 'electric', 'billing_period_from': '2022-02-02', 'billing_period_to': '2022-03-04', 'consumption': 60800000, 'tariff': 'EL9 General Large'},
            #     {'id': '000000000', 'type': 'electric', 'billing_period_from': '2022-02-02', 'billing_period_to': '2022-03-04', 'consumption': 66400000, 'tariff': 'EL9 General Large'}
            # ])

    # @unittest.skip("Skipping this test for now")
    def test_con_edison_with_none_amount(self):
        with open("../bill_pdfs/con_edison/none_amount.pdf", "rb") as bill:
            parsed_values = ConEdison.parse_bill(bill)
            self.assertEqual(parsed_values["account_number"], "000000000000000")
            self.assertEqual(parsed_values["billed_on"], "2022-07-05")
            self.assertEqual(parsed_values["outstanding_balance"], 0)
            self.assertEqual(parsed_values["billing_period_from"], None)
            self.assertEqual(parsed_values["billing_period_to"], None)
            self.assertEqual(parsed_values["total_amount"], 0)
            # self.assertEqual(parsed_values["electricity_consumption"], None)
            self.assertEqual(parsed_values["delivery_charge"], None)
            self.assertEqual(parsed_values["supply_charge"], None)
            # self.assertEqual(parsed_values["community_solar_bill_credit"], None)
            # self.assertEqual(parsed_values["meters"], [])

    # @unittest.skip("Skipping this test for now")
    def test_con_edison_with_none_amount_with_adjustment(self):
        with open("../bill_pdfs/con_edison/none_amount_with_adjustment.pdf", "rb") as bill:
            parsed_values = ConEdison.parse_bill(bill)
            self.assertEqual(parsed_values["account_number"], "000000000000000")
            self.assertEqual(parsed_values["billed_on"], "2022-07-11")
            self.assertEqual(parsed_values["outstanding_balance"], -3679)
            self.assertEqual(parsed_values["billing_period_from"], None)
            self.assertEqual(parsed_values["billing_period_to"], None)
            self.assertEqual(parsed_values["total_amount"], 0)
            # self.assertEqual(parsed_values["electricity_consumption"], None)
            self.assertEqual(parsed_values["delivery_charge"], None)
            self.assertEqual(parsed_values["supply_charge"], None)
            # self.assertEqual(parsed_values["community_solar_bill_credit"], None)
            # self.assertEqual(parsed_values["meters"], [])
    
    # @unittest.skip("Skipping this test for now")
    def test_con_edison_with_none_amount_with_consumption(self):
        with open("../bill_pdfs/con_edison/none_amount_with_consumption.pdf", "rb") as bill:
            parsed_values = ConEdison.parse_bill(bill)
            self.assertEqual(parsed_values["account_number"], "000000000000000")
            self.assertEqual(parsed_values["billed_on"], "2022-08-09")
            self.assertEqual(parsed_values["outstanding_balance"], -397928)
            self.assertEqual(parsed_values["billing_period_from"], "2020-03-19")
            self.assertEqual(parsed_values["billing_period_to"], "2022-08-08")
            self.assertEqual(parsed_values["total_amount"], 0)
            # self.assertEqual(parsed_values["electricity_consumption"], 120000)
            self.assertEqual(parsed_values["delivery_charge"], 85689)
            self.assertEqual(parsed_values["supply_charge"], 1071)
            # self.assertEqual(parsed_values["community_solar_bill_credit"], None)
            # self.assertEqual(parsed_values["meters"], [{'id': '000000000', 'type': 'electric', 'billing_period_from': '2020-03-19', 'billing_period_to': '2022-08-08', 'consumption': 120000, 'tariff': 'EL2 Small Non-Residential'}])

if __name__ == '__main__':
    unittest.main()