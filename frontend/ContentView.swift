//
//  ContentView.swift
//  SmartDine
//
//  Created by Evan Velek on 2/9/26.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            Tab(Constants.homeString, systemImage: Constants.homeIcon){
                HomeView()
            }
            Tab(Constants.favoriteString, systemImage:Constants.favoriteIcon){
                Text(Constants.upcomingString)
            }
            Tab(Constants.settingsString, systemImage:Constants.settingsIcon){
                Text(Constants.settingsString)
            }
        }
    }
}

#Preview {
    ContentView()
}
