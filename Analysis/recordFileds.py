#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#car2go
car2go_bookings_cols = [
    "_id",
    "init_fuel",
    "city" ,
    "walking",
    "vendor",
    "driving",
    "final_time",
    "plate",
    "engineType",
    "init_time" ,
    "vin",
    "smartPhoneRequired",
    "interior",
    "final_fuel",
    "exterior",
    "init_date",
    "final_date",
    "init_address",
    "final_address",
    "origin_destination",
    "public_transport"
    ]

car2go_parkings_cols=[
    "_id",
    "plate" ,
    "vendor",
    "final_time" ,
    "loc",
    "init_time" ,
    "vin",
    "smartPhoneRequired",
    "interior",
    "exterior",
    "address",
    "init_date",
    "final_date",
    "city",
    "fuel",
    "engineType"
]
walking_cols=["duration", "distance"]
driving_cols=["duration", "distance"]
origin_destination_cols = ["type", "coordinates"]
public_transport_cols = ["duration","destination", "arrival_date", "arrival_time"]

enjoy_bookings_cols = [
    "_id",
    "init_fuel",
    "virtual_rental_type_id",
    "walking" ,
    "final_time",
    "final_fuel",
    "init_date",
    "final_date",
    "final_address",
    "city",
    "driving",
    "carModelData",
    "plate",
    "vendor",
    "car_category_id",
    "init_time",
    "car_category_type_id",
    "car_name",
    "onClick_disabled",
    "origin_destination",
    "init_address" ,
    "virtual_rental_id",
    "public_transport"
]

enjoy_parkings_col = [
    "_id",
    "city",
    "vendor",
    "final_time",
    "plate",
    "car_category_id",
    "init_time",
    "car_category_type_id",
    "virtual_rental_type_id",
    "carModelData",
    "car_name",
    "init_date",
    "onClick_disabled",
    "virtual_rental_id",
    "fuel",
    "final_date",
    "loc",
    "address"
]


