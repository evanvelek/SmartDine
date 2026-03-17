//
//  Profile.swift
//  SmartDine
//
//  Created by Evan Velek on 3/12/26.
//

import Foundation

func saveUserApi(qr: QuizResult, userId: String, allergyString: String) async {
    guard let url = URL(string: "\(Constants.apiRoot)/profile") else {
        return
    }

    let body: [String: Any] = [
        "user_id": userId,
        "diet_restrictions": allergyString,
        "preferred_cuisines": qr.preferedCuisines ?? "",
        "budget_max_price_level": qr.budgetMaxPriceLevel ?? 2,
        "dining_style": "casual",
        "max_distance_m": qr.maxDistanceM ?? 2000,
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
