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
    
}
