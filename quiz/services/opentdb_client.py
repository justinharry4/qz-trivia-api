import time, logging, json
import requests


logger = logging.getLogger(__name__)


class APIClientError(Exception):
    def __init__(self, message="Error occured while fetching quiz data"):
        return super().__init__(message)


class OpenTDBClient:
    BASE_URL = "https://opentdb.com"
    TIMEOUT = 30  # seconds
    RETRIES = 3

    # Success code
    SUCCESS = 0

    # Error codes
    AMOUNT_TOO_LARGE = 1
    INVALID_PARAM = 2
    INVALID_TOKEN = 3
    SPENT_TOKEN = 4
    TOO_MANY_REQUESTS = 5

    def __init__(self):
        self.first_use = True
        self.session_token = None
        self.delay = 6  # seconds

    def call_endpoint(self, path, params=None):
        if not self.first_use:
            time.sleep(self.delay)
        else:
            self.first_use = False

        logger.debug(
            f"Calling OpenTDB API - METHOD: GET - "
            f"URL: {self.BASE_URL + path} - "
            f"PARAMS: {params}"
        )
        response = requests.get(
            self.BASE_URL + path, params=params, timeout=self.TIMEOUT
        )
        response.raise_for_status()
        return response.json()

    def call_endpoint_safely(self, path, params=None):
        for trial in range(self.RETRIES + 1):
            try:
                result = self.call_endpoint(path, params=params)
                tdb_response_code = result.get("response_code")

                if tdb_response_code:
                    if tdb_response_code == self.SUCCESS:
                        return result
                    elif tdb_response_code == self.TOO_MANY_REQUESTS:
                        if trial == self.RETRIES:
                            logger.warning(
                                f'OpenTDB request unsuccessful - PATH: {path} - '
                                f'PARAMS: {params} - reason: Too many requests'
                            )
                            raise APIClientError()

                        self.delay = self.delay * 2
                        continue
                    else:
                        logger.error(
                            f'OpenTDB request unsuccessful - PATH: {path} - '
                            f'PARAMS: {params} - reason: not specified'
                        )
                        raise APIClientError()

                return result
            except requests.exceptions.RequestException:
                logger.error(
                    f'OpenTDB request failed - PATH: {path} - '
                    f'PARAMS: {params}',
                    exc_info=True
                )
                raise APIClientError()

    def get_categories(self):
        logger.info('Fetching OpenTDB global category count data')
        global_count_result = self.call_endpoint_safely("/api_count_global.php")

        logger.info('Fetching OpenTDB category data')
        category_result = self.call_endpoint_safely("/api_category.php")

        categories = category_result["trivia_categories"]

        for category in categories:
            cat_id = str(category["id"])
            question_count_data = global_count_result["categories"][cat_id]
            questions_count = question_count_data["total_num_of_verified_questions"]
            category["questions_count"] = questions_count

        return categories

    def set_token(self):
        params = {"command": "request"}
        result = self.call_endpoint_safely("/api_token.php", params=params)

        self.session_token = result["token"]

    def get_questions_for_category(self, category_id, amount):
        params = {
            "amount": amount,
            "category": category_id,
            "token": self.session_token,
        }

        logger.info(
            f'Fetching OpenTDB question data - OpenTDB Category ID: {category_id}'
        )
        result = self.call_endpoint_safely("/api.php", params=params)

        return result["results"]
