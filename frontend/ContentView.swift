//
//  ContentView.swift
//  SmartDine
//
//  Created by Evan Velek on 2/9/26.
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var session: UserSession
    var body: some View {
        TabView {
            Tab(Constants.homeString, systemImage: Constants.homeIcon) {
                HomeView().environmentObject(session)
            }
            Tab(Constants.favoriteString, systemImage: Constants.favoriteIcon) {
                Text(Constants.upcomingString)
                // FavoritesView().environmentObject(session)
            }
            Tab(Constants.settingsString, systemImage: Constants.settingsIcon) {
                SettingsView().environmentObject(session)
            }
        }
    }
}

#Preview {
    ContentView()
}
