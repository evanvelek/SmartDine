//
//  Visit.swift
//  SmartDine
//
//  Created by Evan Velek on 3/12/26.
//

import Foundation

func visitApi(
    userId: String,
    restaurantId: String,
    visitRating: Int,
    mealType: String
) async {
    guard let url = URL(string: "\(Constants.apiRoot)/visit") else {
        return
    }

    let body: [String: Any] = [
        "user_id": userId,
        "restaurant_id": restaurantId,
        "timestamp": ISO8601DateFormatter().string(from: Date()),
        "visit_rating": visitRating,
        "context": [
            "day_of_week": Calendar.current.component(.weekday, from: Date()),
            "meal_type": mealType,
        ],
    ]
    do {
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, _) = try await URLSession.shared.data(for: request)
        let decoder = JSONDecoder()

        decoder.keyDecodingStrategy = .convertFromSnakeCase

        return

    } catch {
        print(error)
    }

    return

}
