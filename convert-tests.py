import unittest
import convert

class TestConvert(unittest.TestCase):
    def test_check_conflicts(self):
        self.assertTrue(convert.check_conflicts("0213",'0100','1234','0100'))
        self.assertFalse(convert.check_conflicts('0213','1000','1034','1000'))
        self.assertTrue(convert.check_conflicts("0413",'1010','0423','1100'))
        self.assertFalse(convert.check_conflicts('0413','1100','1034','0101'))
        self.assertTrue(convert.check_conflicts("0423",'1001','0213','0110'))
        self.assertFalse(convert.check_conflicts('0423','1001','1024','0110'))
    def test_update_action(self):
        self.assertEqual('0001', convert.update_action("1000", "0001"))
        self.assertEqual('0101', convert.update_action('0011', '0101'))
        self.assertEqual('2100', convert.update_action('2010', '0100'))
        self.assertEqual('0011', convert.update_action('0102', '0013'))
if __name__=='__main__':
    unittest.main()
