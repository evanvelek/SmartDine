//
//  Restaurant.swift
//  SmartDine
//
//  Created by Evan Velek on 2/12/26.
//

import Foundation

//"name": "string",
//      "lat": 0,
//      "lng": 0,
//      "categories": [],
//      "price_level": 0,
//      "rating": 0,
//      "reviews_count": 0,
//      "is_open_now": true,
//      "address": "string",
//      "distance_m": 0,
//      "eta_min": 0,
//      "raw": {
//        "additionalProp1": {}
//      },
//      "explanation": ""

struct Restaurant: Identifiable, Hashable {
    let id = UUID()
    let name: String
    let priceLevel: Int
    let rating: Double
    let isOpenNow: Bool
    let distanceM: Int
    let etaMin: Int
    let explanation: String
}
