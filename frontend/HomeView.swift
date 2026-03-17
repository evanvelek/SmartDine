//
//  HomeView.swift
//  SmartDine
//
//  Created by Evan Velek on 2/9/26.
//

import SwiftUI
internal import _LocationEssentials

enum TravelMode: CaseIterable {
    case walking, driving, biking

    var label: String {
        switch self {
        case .walking: return "Walk"
        case .driving: return "Drive"
        case .biking:  return "Bike"
        }
    }

    var icon: String {
        switch self {
        case .walking: return "figure.walk"
        case .driving: return "car.fill"
        case .biking:  return "bicycle"
        }
    }
}

struct HomeView: View {
    @EnvironmentObject var session: UserSession
    @StateObject private var locationManager = LocationManager()

    @State private var searchText = ""
    @State private var favorites: [Restaurant] = []
    @State private var selectedMode: TravelMode = .walking
        

    func updateFavorites(lat: Double, lng: Double) async {
        self.favorites = await session.getUserRecommendations(
            lat: lat,
            lng: lng,
            with: searchText
        )
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Travel mode toggle
                TravelModePicker(selected: $selectedMode)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(Color(.systemGroupedBackground))

                Divider()

                List(favorites) { restaurant in
                    NavigationLink(value: restaurant) {
                        RestaurantRow(restaurant: restaurant)
                    }
                    .listRowInsets(EdgeInsets(top: 10, leading: 16, bottom: 10, trailing: 16))
                }
                .listStyle(.plain)
            }
            .navigationTitle("Restaurants")
            .navigationBarTitleDisplayMode(.large)
            .searchable(text: $searchText, prompt: "Search restaurants…")
            .onSubmit(of: .search) {
                if let coords = locationManager.location {
                    Task {
                        await updateFavorites(lat: coords.latitude, lng: coords.longitude)
                    }
                }
            }
            .onChange(of: selectedMode) {
                if let coords = locationManager.location {
                    Task { await updateFavorites(lat: coords.latitude, lng: coords.longitude) }
                }
            }
            .navigationDestination(for: Restaurant.self) { restaurant in
                RestaurantDetailView(restaurant: restaurant)
            }
        }
        .onAppear {
            locationManager.requestLocation()
        }
    }
}

struct TravelModePicker: View {
    @Binding var selected: TravelMode

    var body: some View {
        HStack(spacing: 8) {
            ForEach(TravelMode.allCases, id: \.self) { mode in
                Button(action: { withAnimation(.spring(response: 0.3)) { selected = mode } }) {
                    HStack(spacing: 6) {
                        Image(systemName: mode.icon)
                            .font(.system(size: 14, weight: .semibold))
                        Text(mode.label)
                            .font(.system(size: 14, weight: .semibold))
                    }
                    .foregroundColor(selected == mode ? .white : .primary)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 9)
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(selected == mode ? Color.accentColor : Color(.secondarySystemGroupedBackground))
                    )
                }
                .buttonStyle(.plain)
            }
        }
    }
}

struct RestaurantRow: View {
    let restaurant: Restaurant

    var body: some View {
        HStack(spacing: 12) {
            // Icon placeholder
            RoundedRectangle(cornerRadius: 10)
                .fill(Color(.secondarySystemGroupedBackground))
                .frame(width: 56, height: 56)
                .overlay(
                    Image(systemName: "fork.knife")
                        .font(.system(size: 22, weight: .medium))
                        .foregroundColor(Color(.tertiaryLabel))
                )

            VStack(alignment: .leading, spacing: 4) {
                Text(restaurant.name)
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(.primary)
                    .lineLimit(1)

                StarRatingView(rating: restaurant.rating)

                PriceLevelView(priceLevel: restaurant.priceLevel)
            }

            Spacer()
        }
        .padding(.vertical, 4)
    }
}

struct StarRatingView: View {
    let rating: Double

    var body: some View {
        HStack(spacing: 2) {
            ForEach(0..<5) { index in
                Image(systemName: starImage(index: index, rating: rating))
                    .font(.system(size: 11))
                    .foregroundColor(.orange)
            }
            Text(String(format: "%.1f", rating))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.secondary)
        }
    }

    func starImage(index: Int, rating: Double) -> String {
        let threshold = Double(index) + 1
        if rating >= threshold { return "star.fill" }
        if rating >= threshold - 0.5 { return "star.leadinghalf.filled" }
        return "star"
    }
}

struct PriceLevelView: View {
    let priceLevel: Int  // 1–4

    var body: some View {
        HStack(spacing: 1) {
            ForEach(0..<4) { index in
                Text("$")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(index < priceLevel ? .green : Color(.quaternaryLabel))
            }
        }
    }
}
#Preview {
    HomeView()
}
