from SeleniumDriver.Driver import Driver
from Scraper.Scraper import Scraper
from Utilities.LogUtil import LogUtil

logger = LogUtil('out.log')

def main():
    log = logger.get_logger("scrape_data")
    log.info("Log Started")
    driver = Driver(logger)
    try:
        scraper = Scraper(driver, logger)
        restaurant_data_dict = scraper.scrape()
        scraper.save(restaurant_data_dict)
    except Exception as e:
        log.exception(e)
    driver.tear_down()

if __name__ == "__main__":
    main()
