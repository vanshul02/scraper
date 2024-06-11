import json
import gzip
from time import sleep
from multiprocessing import Pool, cpu_count

from Utilities.LogUtil import LogUtil
from SeleniumDriver.Driver import Driver
from constant.constant import *
from selenium.webdriver.common.by import By
from seleniumwire.utils import decode as sw_decode


def get_restaurant_dict_helper(restaurant):
    key = restaurant.get("chainID", restaurant["address"]["name"])
    data_dictionary = {
        "restaurant_name": restaurant.get("chainName", None),
        "latitude_longitude": restaurant.get("latlng", {}),
        "cuisine": restaurant.get("merchantBrief", {}).get("cuisine", []),
        "rating": restaurant.get("merchantBrief", {}).get("rating", None),
        "estimate_time_of_delivery": restaurant.get("estimatedDeliveryTime", None),
        "distance_from_delivery": restaurant.get("merchantBrief", {}).get(
            "distanceInKm", None
        ),
        "image_link": restaurant.get("merchantBrief", {}).get("photoHref"),
        "has_promo": restaurant.get("merchantBrief", {})
        .get("promo", {})
        .get("hasPromo", False),
        "id": restaurant.get("id", None),
        "estimated_delivery_fee": restaurant.get("estimatedDeliveryFee", {}).get(
            "priceDisplay", None
        ),
        "promo_list": [
            promo["displayedText"]
            for promo in restaurant.get("sideLabels", {}).get("data", [])
        ],
    }
    return key, data_dictionary


class Scraper:

    def __init__(self, driver: Driver, logger: LogUtil) -> None:
        self.driver = driver
        self.log = logger.get_logger("Scraper")
        self._init_request()

    def _init_request(self):
        # This function is responsible to search and select the given address on the website
        # and then click on search button
        self.driver.browser.get(BASE_URL)
        sleep(HIGH_SLEEP)

        #Finding the input field
        location_input = self.driver.browser.find_element(value=LOCATION_INPUT_BOX_ID)
        location_input.send_keys(SEARCH_VALUE)
        sleep(MED_SLEEP) # Wait till location options are loaded

        #Select the appropriate Location from List
        list_item_option = self.driver.browser.find_element(
            By.XPATH,
            "//li[text()='Chong Boon Dental Surgery - Block 456 Ang Mo Kio Avenue 10, #01-1574, Singapore, 560456']",
        )
        list_item_option.click()

        #Find and click the search button
        search_button = self.driver.browser.find_element(
            By.CLASS_NAME, SEARCH_BUTTON_CLASS_NAME
        )
        search_button.click()
        sleep(V_HIGH_SLEEP)

    def infinite_scroll(self):
        last_height = self.driver.browser.execute_script(
            "return document.body.scrollHeight"
        )
        for i in range(8):
            # Since we need to get 200 results minimum and
            # each request consists nearly 32 entries we need to make 8 iterations
            self.log.info(f"Scrolling Iteration {i + 1}")
            self.driver.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight)"
            )
            sleep(MED_SLEEP)
            new_height = self.driver.browser.execute_script(
                "return document.body.scrollHeight"
            )
            if new_height == last_height:
                break

    def fetch_search_response(self):
        #This function is responsible for iterating through each request made by
        #the browser and fetch and decode all the POST request made to SEARCH_URL
        search_data = []
        for req in self.driver.browser.iter_requests():
            if req.method == SEARCH_REQUEST_TYPE and req.url == SEARCH_URL:
                self.log.info(f"{req}")
                data = sw_decode(
                    req.response.body,
                    req.response.headers.get(HEADER_CONTENT_ENCODING, IDENTITY),
                )
                data = data.decode(ENCODING)
                try:
                    data = json.loads(data)
                    search_data.append(data)
                except (
                    Exception
                ) as e:  # If any of the 8 iterations did not recieve 200 response
                    self.log.exception(e)
        self.log.info(f"Search Data Len: {len(search_data)}")
        return search_data

    def get_restaurant_data_dict(self, search_data):
        #This function is asynchronously calling the transformer function and 
        #transforming decoded data into a more readble JSON
        restaurant_data_dict = {}
        data_dict = {}
        for i in range(len(search_data)):
            search_result = search_data[i]
            self.log.info(f"Processing Iteration {i + 1}")
            restaurant_list = search_result["searchResult"]["searchMerchants"]

            with Pool(cpu_count()) as p:  # MultiProcessing
                results = p.map(get_restaurant_dict_helper, restaurant_list)
            data_dict.update({key: value for key, value in results})
            self.log.info(f"Completed Processing Iteration {i + 1}")
            self.log.info(f"Scraped {len(results)} restaurants in this iteration")
            self.log.info(
                f"Scraped {len(data_dict.keys())} distinct restaurants till this iteration"
            )
        self.log.info(f"Scraped {len(data_dict.keys())} restaurants overall")
        restaurant_data_dict["total_restaurants"] = len(data_dict.keys())
        restaurant_data_dict["restaurants_data"] = data_dict
        return restaurant_data_dict

    def scrape(self):
        self.infinite_scroll()
        search_result = self.fetch_search_response()
        restaurants_data_dict = self.get_restaurant_data_dict(search_result)
        return restaurants_data_dict

    def save(self, restaurants_data_dict):
        with open("grab_restaurants.json", "w") as f:
            json.dump(
                restaurants_data_dict, f, indent=4
            )  # For testing and clear visibility, letting it stay for the assignment purpose
        self.log.info("Successfully Written JSON file")
        with gzip.open(OUTPUT_FILE_NAME, "w") as f:
            f.write(json.dumps(restaurants_data_dict).encode(ENCODING))
        self.log.info("Successfully Written GZIP file")
