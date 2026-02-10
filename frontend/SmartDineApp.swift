//
//  SmartDineApp.swift
//  SmartDine
//
//  Created by Evan Velek on 2/9/26.
//

import SwiftUI

@main
struct SmartDineApp: App {
    
    @StateObject private var session = UserSession()
    
    var body: some Scene {
        WindowGroup {
            if session.userId == nil {
                NewUserQuiz().environmentObject(session)
            } else {
                ContentView().environmentObject(session)
            }
        }
    }
}


