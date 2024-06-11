import logging
from seleniumwire import webdriver
from seleniumwire.handler import log
from seleniumwire.server import logger
log.setLevel(logging.WARN)
logger.setLevel(logging.WARN)
#Setting log level to warn here so that my logs are not mixed with logs of seleniumwire


class Driver:
    def __init__(self, logger) -> None:
        self.browser = None
        self.log = logger.get_logger("Driver")
        self.setup()

    def setup(self):
        #Here we are creating some options to handle the web driver properties
        # Headless doesn't launch the firefox browser on machine and hence promotes scalability by reducing GPU usage


        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--headless") 
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-extensions")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--disable-proxy-certificate-handler")
        firefox_options.add_argument('--allow-running-insecure-content')
        firefox_options.add_argument('--ignore-certificate-errors-spki-list')
        firefox_options.add_argument("--ignore-certificate-errors")
        firefox_options.add_argument('--ignore-ssl-errors')

        #We are exculding some hosts to ignore the ssl errors

        options = {
            "exclude_hosts": [
                "www.google.com",
                "accounts.google.com",
                "ad.doubleclick.net",
                "content-autofill.googleapis.com",
                "connect.facebook.net",
                "www.google-analytics.com",
                "vc.hotjar.io",
                "td.doubleclick.net",
                "google-analytics.com",
                "analytics.google.com",
                "google.com",
                "facebook.com",
                "stats.g.doubleclick.net",
            ]
        }

        self.browser = webdriver.Firefox(options=firefox_options, seleniumwire_options=options)
        self.log.info("Firefox Driver Created")

    def tear_down(self):
        self.browser.quit()
        self.log.info("Firefox Driver Quit")