//
//  Recommend.swift
//  SmartDine
//
//  Created by Evan Velek on 2/15/26.
//

import Foundation
import SwiftUI
internal import _LocationEssentials

struct ApiResponse: Codable {
    let recommendations: [ApiRecommendation]
}

struct ApiRecommendation: Codable {
    let id: String
    let name: String?
    let priceLevel: Int?
    let rating: Double?
    let isOpenNow: Bool?
    let distanceM: Double?
    let etaMin: Int?
    let explanation: String?
}

func recommend(lat: Double, lng: Double, with session: UserSession) async -> ApiResponse {
    
    @AppStorage("max_distance_m") var max_distance_m: Int = 2000
    @AppStorage("transport_mode") var transport_mode: String = "walk"

    guard let url = URL(string: "\(Constants.apiRoot)/recommend") else {
        return ApiResponse(recommendations: [])
    }
    

    let body: [String: Any] = [
        "user_id": session.userId ?? "0",
        "context": [
            "lat": lat,
            "lng": lng,
            "time_available_min": 30,
            "max_distance_m": max_distance_m,
            // "time_of_day": "breakfast",
            "transport_mode": transport_mode,
        ],
    ]
    print(body)

    do {
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, _) = try await URLSession.shared.data(for: request)
        let decoder = JSONDecoder()
        
        decoder.keyDecodingStrategy = .convertFromSnakeCase

        return try decoder.decode(ApiResponse.self, from: data)

    } catch {
        print(error)
    }
    
    return ApiResponse(recommendations: [])
}
