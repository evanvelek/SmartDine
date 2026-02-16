//
//  HomeView.swift
//  SmartDine
//
//  Created by Evan Velek on 2/9/26.
//

import SwiftUI
internal import _LocationEssentials

struct HomeView: View {
    @EnvironmentObject var session: UserSession
    @StateObject private var locationManager = LocationManager()

    @State private var searchText = ""

    @State private var favorites: [Restaurant] = []

    func updateFavorites(lat: Double, lng: Double) async {
        self.favorites = await session.getUserRecommendations(
            lat: lat,
            lng: lng,
            with: searchText
        )
    }

    var body: some View {
        NavigationStack {
            List(favorites) { favorite in
                NavigationLink(value: favorite) {
                    HStack {
                        HStack(spacing: 2) {
                            ForEach(0..<5) { index in
                                Image(systemName: starImage(index: index, rating: favorite.rating))
                                    .foregroundColor(.yellow)
                            }
                        }
                        Text(favorite.name)
                    }
                    .frame(height: 80)
                }
            }
            .navigationTitle("Restaurants") // This title will now sit at the top of the whole view
            .searchable(text: $searchText, prompt: "Enter exact query")
            .onSubmit(of: .search) {
                if let coords = locationManager.location {
                    Task {
                        await updateFavorites(lat: coords.latitude, lng: coords.longitude)
                    }
                }
            }
            .navigationDestination(for: Restaurant.self) { restaurant in
                VStack {
                    Text(restaurant.name).font(.headline)
                    Text(restaurant.explanation).font(.body)
                }
            }
        }
        .onAppear {
            locationManager.requestLocation()
        }
    }
}

#Preview {
    HomeView()
}
