from database import Database
from typing import List
from pymongo import MongoClient


class TravelyoMaster:
    def __init__(self, hotel_id=None, hotel_name=None, city_name=None):
        self.hotel_id = hotel_id
        self.hotel_name = hotel_name
        self.city_name = city_name

    @classmethod
    def pull_data(cls, hotel_ids: List[str]):
        objs = []
        db = Database(instance="travelyo", db_name="travelyo_master_v4")
        sql = f"""
        SELECT hfp.hotel_id, hfp.hotel_name, hfgd.city_name
        FROM hf_property hfp 
        INNER JOIN hf_property_to_global_destination hfptgd ON hfptgd.recomended_hotel_id = hfp.id
        INNER JOIN hf_global_destination hfgd ON hfgd.id = hfptgd.global_destination_id 
        WHERE hfp.hotel_id in {tuple(hotel_ids)}
        """
        resp = db.fetch(sql)
        for row in resp:
            objs.append(cls(hotel_id=row[0], hotel_name=row[1], city_name=row[2]))
        return objs


class MongoHotelInnstant:
    def __init__(
        self,
        hotel_id=None,
        hotel_name=None,
        stars=None,
        address=None,
        city_name=None,
        country_name=None,
        room_count=None,
    ):
        self.hotel_id = hotel_id
        self.hotel_name = hotel_name
        self.stars = stars
        self.address = address
        self.city_name = city_name
        self.country = country_name
        self.room_count = room_count

    @classmethod
    def pull_data(cls, hotel_ids: List[str]) -> List["MongoHotelInnstant"]:
        client = MongoClient("mongodb://mongo-main-shard-00-00.travelyo-cdn.site:27027")
        hotel_innstant_collection = client["travelyo_smartair"]["HotelInnstant"]
        query = {"hotel_id": {"$in": hotel_ids}}
        resp = hotel_innstant_collection.find(query)
        objs = []
        for r in resp:
            objs.append(
                cls(
                    hotel_id=r.get("hotel_id"),
                    hotel_name=r.get("hotel_name"),
                    stars=r.get("rating"),
                    address=r.get("address"),
                    city_name=r.get("city", {}).get("cityName"),
                    country_name=r.get("city", {}).get("countryName"),
                )
            )
        return objs

    @staticmethod
    def get_hotel_by_id(
        objs: List["MongoHotelInnstant"], hotel_id: str
    ) -> "MongoHotelInnstant":
        for obj in objs:
            if obj.hotel_id == hotel_id:
                return obj
        return None


# class MongoExpediaHotel:
#     def __init__(self):
#         self.hotel_id = None
#         self.expedia_hotel_id = None


class BookingCom:
    def __init__(self, hotel_id=None, booking_com_id=None):
        self.hotel_id = hotel_id
        self.booking_com_id = booking_com_id
        self.facilities = []
        self.description = None
        self.reviews = []

        if self.hotel_id and self.booking_com_id:
            self.pull_reviews_facilities_description()

    def print(self):
        print(vars(self))

    @staticmethod
    def get_mapping(hotel_ids: List[str]):
        """This method pulls the mapping of booking.com"""
        db = Database(instance="travelyo", db_name="travelyo_master_v4")
        sql = f"""
                SELECT travolutionary_id, bkn_id
                FROM gim_hotels_mapper
                WHERE travolutionary_id IN {tuple(hotel_ids)} AND bkn_id IS NOT NULL
                """
        resp = db.fetch(sql)
        return resp

    def get_description(self):
        """This method pulls the descriptions of booking.com based on the hotel ids provided"""
        db = Database(instance="move_cx_1", db_name="booking_com")
        sql = f"""
            SELECT * FROM hotel_descriptions 
            WHERE booking_com_hotel_id = {self.booking_com_id}
            """
        print(sql)
        resp = db.fetch(sql)
        self.description = resp[0][1] if len(resp) > 0 else None

    def get_reviews(self) -> None:
        """This method pulls the reviews of booking.com based on the hotel id provided"""
        db = Database(instance="move_cx_1", db_name="booking_com")
        sql = f"""
        SELECT review_title, pros, cons, travel_purpose, traveler_type, average_score
        FROM hotel_reviews
        WHERE booking_com_hotel_id = {self.booking_com_id} 
        """
        print(sql)
        resp = db.fetch(sql)
        for r in resp:
            self.reviews.append(
                {
                    "review_title": r[0],
                    "pros": r[1],
                    "cons": r[2],
                    "travel_purpose": r[3],
                    "traveler_type": r[4],
                    "average_score": r[5],
                }
            )

    def get_facilities(self) -> None:
        db = Database(instance="move_cx_1", db_name="booking_com")
        sql = f"""
        SELECT facility_name 
        FROM hotel_facilities
        WHERE booking_com_hotel_id = {self.booking_com_id} 
        """
        resp = db.fetch(sql)
        self.facilities = [r[0] for r in resp]

    def pull_reviews_facilities_description(self) -> None:
        self.get_reviews()
        self.get_facilities()
        self.get_description()

    @staticmethod
    def map_description_to_hotel(hotel_objs: List["BookingCom"], descriptions):
        """This method gets as args a list of BookingCom hotel object and the list of descriptions and assigns the
        description to each hotel"""
        for hotel in hotel_objs:
            for description in descriptions:
                if str(hotel.booking_com_id) == str(description[0]):
                    hotel.description = description[1]

    @classmethod
    def pull_data(cls, hotel_ids: List[str]) -> List["BookingCom"]:
        objs = []
        mapping = cls.get_mapping(hotel_ids)
        for hotel in mapping:
            objs.append(cls(hotel_id=hotel[0], booking_com_id=hotel[1]))
        return objs

    @classmethod
    def get_hotel_by_id(cls, objs: List["BookingCom"], hotel_id: str) -> "BookingCom":
        for obj in objs:
            if str(obj.hotel_id) == str(hotel_id):
                return obj
        return cls()


if __name__ == "__main__":
    objs = BookingCom.pull_data(hotel_ids=["5300384", "4112419"])
    for o in objs:
        o.print()
