//
//  Favorites.swift
//  SmartDine
//
//  Created by Evan Velek on 3/17/26.
//

import Foundation

func addFavoriteApi(
    userId: String,
    restaurantId: String,
    restaurantName: String,
    restaurantAddress: String,
    rating: Double,
    description: String
) async {
    guard let url = URL(string: "\(Constants.apiRoot)/favorites") else {
        return
    }

    let body: [String: Any] = [
        "user_id": userId,
        "restaurant_id": restaurantId,
        "name": restaurantName,
        "address": restaurantAddress,
        "rating": rating,
        "description": description
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

struct ApiFavorites: Codable {
    let favorites: [ApiFavorite]
}

struct ApiFavorite: Codable, Hashable {
    let id: String
    let name: String?
    let address: String?
    let rating: Double?
    let description: String?
}

func getFavoritesApi(userId: String) async -> ApiFavorites {
    do {
        var request = URLRequest(url: URL(string:"\(Constants.apiRoot)/favorites/\(userId)")!)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let (data, _) = try await URLSession.shared.data(for: request)
        let decoder = JSONDecoder()

        decoder.keyDecodingStrategy = .convertFromSnakeCase

        return try decoder.decode(ApiFavorites.self, from: data)

    } catch {
        print(error)
    }
    
    return ApiFavorites(favorites: [])
    
    
}
