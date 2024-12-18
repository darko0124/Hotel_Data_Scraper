from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import psycopg2

def main():
    checkin_date = input("Check-in date (YYYY-MM-DD) :")
    checkout_date = input("Check-out date (YYYY-MM-DD) :")
    city = input("Enter city : ")
    num_of_rooms = int(input("Enter number of rooms : "))
    num_of_adults = int(input("Enter number of adults : "))
    num_of_children = int(input("Enter number of children : "))

    #calculate number of nights
    checkin = datetime.strptime(checkin_date, '%Y-%m-%d')
    checkout = datetime.strptime(checkout_date, '%Y-%m-%d')
    num_of_nights = (checkout-checkin).days

    page_url = f'https://www.booking.com/searchresults.en-gb.html?ss={city}&ssne={city}&ssne_untouched={city}&efdco=1&label=gen173nr-1BCAEoggI46AdIM1gEaBeIAQGYAQm4ARfIAQ_YAQHoAQGIAgGoAgO4AvmmhrsGwAIB0gIkZTM3MTQ1YjMtZjBhNS00ZDQxLTgwY2MtY2M2NDUyYTdhMWE12AIF4AIB&sid=10c53660167ef8e8af09486149c271c7&aid=304142&lang=en-gb&sb=1&src_elem=sb&src=index&dest_id=-121726&dest_type={city}&checkin={checkin_date}&checkout={checkout_date}&group_adults={num_of_adults}&no_rooms={num_of_rooms}&group_children={num_of_children}&no_nights={num_of_nights}'

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(page_url, timeout=60000)
            hotels_list = []
            hotels = page.locator('//div[@data-testid="property-card"]').all()
            total_hotels = len(hotels)
            print(f'There are {total_hotels} hotels found.')

            for hotel in hotels:
                hotel_dict = {
                    'hotel': hotel.locator('//div[@data-testid="title"]').inner_text(),
                    f'price_for_{num_of_nights}_nights': hotel.locator(
                        '//div[@data-testid="price-and-discounted-price"]').inner_text() if hotel.locator(
                        '//div[@data-testid="price-and-discounted-price"]').is_visible() else "Not Available",
                    'score': hotel.locator('//div[@data-testid="review-score"]/div[1]').inner_text() if hotel.locator(
                        '//div[@data-testid="review-score"]').is_visible() else "Not Available",
                    'reviews_count': hotel.locator(
                        '//div[@data-testid="review-score"]/div[2]/div[2]').inner_text() if hotel.locator(
                        '//div[@data-testid="review-score"]').is_visible() else "Not Available"
                }
                hotels_list.append(hotel_dict)

            df = pd.DataFrame(hotels_list)
            df.to_csv('hotels_list.csv', index=False)

        finally:
            browser.close()

config_file_path = 'DB_Config.txt'

with open(config_file_path, 'r') as config_file:
    config_lines = config_file.readlines()

    DB_USER = config_lines[0].strip()
    DB_PASSWORD = config_lines[1].strip()
    DB_HOST = config_lines[2].strip()
    DB_PORT = config_lines[3].strip()
    DB_NAME = config_lines[4].strip()

    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        print("Connection established !")

        # Declare schema and table
        schema_name = "Hotel_data"
        table_name = "hotel_data"


    except (Exception, psycopg2.Error) as error:
        print(f"Error connecting to the PostgreSQL database: {error}")
        connection = None

    #Send the CSV to the DB

    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    main()
