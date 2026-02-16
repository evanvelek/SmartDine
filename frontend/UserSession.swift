//
//  UserSession.swift
//  SmartDine
//
//  Created by Evan Velek on 2/9/26.
//

import Foundation
import Combine


final class UserSession: ObservableObject {
    @Published var userId: String?
    
    init() {
        userId = UserDefaults.standard.string(forKey: "userId")
    }
    
    func saveUser(with quizDat: QuizResult) {
        let newId = UUID().uuidString
        UserDefaults.standard.set(newId, forKey: "userId")
        userId = newId
        
        // TODO: Evan -- Call some sort of save API to backend with new user entry
    }
    
    func deleteUser() {
        userId = nil
    }
    
    func getUserPreferences() -> [String: Int]{
        // TODO: Evan -- Implement backend information retrieval for user
        return [:]
    }
    
    func getUserRecommendations(lat: Double, lng: Double, with query: String) async -> [Restaurant]{
        // TODO: Evan -- implenet backend retrieval
        let data = await recommend(lat: lat, lng: lng, with: self)
        
        let restaurants: [Restaurant] = data.recommendations.map { item in
            Restaurant(
                name: item.name ?? "",
                priceLevel: item.priceLevel ?? 0,
                rating: Double(item.rating ?? 0.0) ,
                isOpenNow: item.isOpenNow ?? false,
                distanceM: Int(item.distanceM ?? 0),
                etaMin: Int(item.etaMin ?? 0),
                explanation: item.explanation ?? ""
            )
        }
        
        return restaurants
    }
    
    func getUserFavorites() -> [Restaurant]{
        // TODO: Evan -- Implement backend retrieval
        return [
            
        ]
    }
    
}
