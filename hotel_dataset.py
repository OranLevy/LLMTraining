import json
from typing import List
from data_sources import MongoHotelInnstant, TravelyoMaster, BookingCom
from pymongo import MongoClient


class Hotel:
    def __init__(self, hotel_id):
        self.hotel_id = hotel_id
        self.hotel_name = None
        self.address = None
        self.city_name = None
        self.country_name = None
        self.description = None
        self.reviews = None
        self.facilities = None

    @classmethod
    def build_objs(cls, hotel_ids: List[str]) -> List["Hotel"]:
        return [cls(hotel_id=id_) for id_ in hotel_ids]

    def update_mongo_data(self, obj: MongoHotelInnstant):
        self.hotel_name = obj.hotel_name
        self.address = obj.address
        self.city_name = obj.city_name
        self.country_name = obj.country

    def update_booking_com_data(self, obj: BookingCom):
        self.description = obj.description
        self.reviews = obj.reviews
        self.facilities = obj.facilities

    def insert_mongo(self):
        client = MongoClient("mongodb://mongo-main-shard-00-00.travelyo-cdn.site:27027")
        llm_collection = client["llm_oran"]["hotel_training_data"]
        data = {
            "hotel_name": self.hotel_name,
            "address": self.address,
            "city_name": self.city_name,
            "country_name": self.country_name,
            "description": self.description,
            "reviews": self.reviews,
            "facilities": self.facilities
        }
        llm_collection.update_one(filter={"hotel_id": self.hotel_id}, update={"$set": data}, upsert=True)

    def check_all_attrs(self):
        """This method checks if all the attributes are defined in order to know if we insert it to mongo or not"""
        return all(
            getattr(self, attr) is not None
            for attr in vars(self)
        )

    def print(self):
        print(vars(self))
