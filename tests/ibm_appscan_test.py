from selenium import webdriver
from selenium.webdriver.support.ui import Select
import unittest
import re
import sys
import os

# importing Product_selenium_unittest as a module
# set relative path
dir_path = os.path.dirname(os.path.realpath(__file__))
try:  # First Try for python 3
    import importlib.util

    product_unit_test_module = importlib.util.spec_from_file_location("product_selenium_unittest",
                                                                      os.path.join(dir_path,
                                                                                   'product_selenium_unittest.py'))  # using ',' allows python to determine the type of separator to use.
    product_unit_test = importlib.util.module_from_spec(product_unit_test_module)
    product_unit_test_module.loader.exec_module(product_unit_test)
except:  # This will work for python2 if above fails
    import imp
    product_unit_test = imp.load_source('product_selenium_unittest',
                                        os.path.join(dir_path, 'product_selenium_unittest.py'))


class IBMAppScanTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome('chromedriver')
        # Allow a little time for the driver to initialize
        self.driver.implicitly_wait(30)
        # Set the base address of the dojo
        self.base_url = "http://localhost:8000/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def login_page(self):
        # Make a member reference to the driver
        driver = self.driver
        # Navigate to the login page
        driver.get(self.base_url + "login")
        # Good practice to clear the entry before typing
        driver.find_element_by_id("id_username").clear()
        # These credentials will be used by Travis when testing new PRs
        # They will not work when testing on your own build
        # Be sure to change them before submitting a PR
        driver.find_element_by_id("id_username").send_keys(os.environ['DD_ADMIN_USER'])
        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys(os.environ['DD_ADMIN_PASSWORD'])
        # "Click" the but the login button
        driver.find_element_by_css_selector("button.btn.btn-success").click()
        return driver

    def test_import_ibm_app_scan_result(self):
        # Login to the site.
        # Username and password will be gotten from environ
        driver = self.login_page()
        # Navigate to the Endpoint page
        driver.get(self.base_url + "product")
        driver.find_element_by_link_text("QA Test").click()
        # "Click" the Finding Drop down
        driver.find_element_by_partial_link_text("Findings").click()
        # "Click" the New Endpoint
        driver.find_element_by_link_text("Import Scan Results").click()
        # Select scan type
        Select(driver.find_element_by_id("id_scan_type")).select_by_visible_text("IBM AppScan DAST")
        # Upload Scan result file
        scanner_file = os.path.join(dir_path, "ibm_appscan_xml_file.xml")
        driver.find_element_by_name("file").send_keys(scanner_file)
        # click on upload button
        driver.find_element_by_css_selector("input.btn.btn-primary").click()
        # Query the site to determine if the finding has been added
        productTxt = driver.find_element_by_tag_name("BODY").text
        # Assert the query to determine status or failure
        self.assertTrue(re.search(r'IBM App Scan processed, a total of 27 findings were processed', productTxt))

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


def suite():
    suite = unittest.TestSuite()
    # Add each test the the suite to be run
    # success and failure is output by the test
    suite.addTest(product_unit_test.ProductTest('test_create_product'))
    suite.addTest(IBMAppScanTest('test_import_ibm_app_scan_result'))
    suite.addTest(product_unit_test.ProductTest('test_delete_product'))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(descriptions=True, failfast=True)
    ret = not runner.run(suite()).wasSuccessful()
    sys.exit(ret)
