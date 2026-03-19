//
//  RestaurantView.swift
//  SmartDine
//
//  Created by Evan Velek on 3/13/26.
//

import Foundation
import SwiftUI

struct FavoriteButton: View {
    let restaurant: Restaurant
    @EnvironmentObject var session: UserSession

    @State private var isFavorited: Bool = false
    @State private var isLoading: Bool = true

    var body: some View {
        Button(action: toggleFavorite) {
            Group {
                if isLoading {
                    ProgressView()
                        .controlSize(.small)
                } else {
                    Image(systemName: isFavorited ? "heart.fill" : "heart")
                        .font(.system(size: 22, weight: .semibold))
                        .foregroundColor(
                            isFavorited ? .red : Color(.secondaryLabel)
                        )
                        .symbolEffect(.bounce, value: isFavorited)
                }
            }
            .frame(width: 28, height: 28)
        }
        .disabled(isLoading)
        .task {
            await loadFavoriteState()
        }
    }

    private func loadFavoriteState() async {
        guard let userId = session.userId else {
            isLoading = false
            return
        }
        let result = await getFavoritesApi(userId: userId)
        isFavorited = result.favorites.contains {
            $0.id == restaurant.id.uuidString
        }
        isLoading = false
    }

    private func toggleFavorite() {
        guard let userId = session.userId else { return }
        let newState = true
        withAnimation(.spring(response: 0.3)) {
            isFavorited = newState
        }
        Task {
            await addFavoriteApi(
                userId: userId,
                restaurantId: restaurant.id.uuidString,
                restaurantName: restaurant.name,
                restaurantAddress: "",
                rating: restaurant.rating,
                description: restaurant.description
            )
        }
    }
}

struct RestaurantDetailView: View {
    let restaurant: Restaurant
    @EnvironmentObject var session: UserSession

    @State private var showVisitSheet = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {

                ZStack(alignment: .bottomLeading) {
                    RoundedRectangle(cornerRadius: 16)
                        .fill(Color(.secondarySystemGroupedBackground))
                        .frame(height: 180)
                        .overlay(
                            Image(systemName: "fork.knife")
                                .font(.system(size: 48, weight: .light))
                                .foregroundColor(Color(.tertiaryLabel))
                        )

                    Label(
                        restaurant.isOpenNow ? "Open Now" : "Closed",
                        systemImage: restaurant.isOpenNow
                            ? "checkmark.circle.fill" : "xmark.circle.fill"
                    )
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(restaurant.isOpenNow ? .green : .red)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(.ultraThinMaterial, in: Capsule())
                    .padding(14)
                }
                .padding(.horizontal, 16)
                .padding(.top, 12)

                HStack(spacing: 12) {
                    Text(restaurant.name)
                        .font(.system(size: 24, weight: .bold))
                    
                    FavoriteButton(restaurant: restaurant)

                    //                    HStack(spacing: 12) {
                    //                        StarRatingView(rating: restaurant.rating)
                    //                        Divider().frame(height: 14)
                    //                        PriceLevelView(priceLevel: restaurant.priceLevel)
                    //                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 16)

                HStack(spacing: 0) {
                    //                    StatTile(
                    //                        icon: "location.fill",
                    //                        value: formattedDistance,
                    //                        label: "Away",
                    //                        color: .blue
                    //                    )
                    //                    Divider().frame(height: 40)
                    //                    StatTile(
                    //                        icon: "clock.fill",
                    //                        value: "\(restaurant.etaMin) min",
                    //                        label: "ETA",
                    //                        color: .orange
                    //                    )
                    //                    Divider().frame(height: 40)
                    StatTile(
                        icon: "star.fill",
                        value: String(format: "%.1f", restaurant.rating),
                        label: "Rating",
                        color: .yellow
                    )
                    Divider().frame(height: 40)
                    StatTile(
                        icon: "dollarsign",
                        value: priceString,
                        label: "Price",
                        color: .green
                    )
                }
                .padding(.vertical, 14)
                .background(Color(.secondarySystemGroupedBackground))
                .cornerRadius(14)
                .padding(.horizontal, 16)
                .padding(.top, 16)

                VStack(alignment: .leading, spacing: 8) {
                    //                    Label("Why we picked this", systemImage: "sparkles")
                    //                        .font(.system(size: 13, weight: .semibold))
                    //                        .foregroundColor(.secondary)

                    Text(restaurant.description)
                        .font(.system(size: 15))
                        .foregroundColor(.primary)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(14)
                .background(Color(.secondarySystemGroupedBackground))
                .cornerRadius(14)
                .padding(.horizontal, 16)
                .padding(.top, 16)

                Button(action: { showVisitSheet = true }) {
                    Label("I visited here", systemImage: "mappin.and.ellipse")
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(Color.accentColor)
                        .cornerRadius(12)
                }
                .padding(.horizontal, 16)
                .padding(.top, 20)
                .padding(.bottom, 32)
            }
        }
        .navigationTitle(restaurant.name)
        .navigationBarTitleDisplayMode(.inline)
        .background(Color(.systemGroupedBackground))
        .sheet(isPresented: $showVisitSheet) {
            LogVisitSheet(restaurant: restaurant)
        }
    }

    private var formattedDistance: String {
        restaurant.distanceM < 1000
            ? "\(restaurant.distanceM)m"
            : String(format: "%.1fkm", Double(restaurant.distanceM) / 1000)
    }

    private var priceString: String {
        String(repeating: "$", count: restaurant.priceLevel)
    }
}

struct StatTile: View {
    let icon: String
    let value: String
    let label: String
    let color: Color

    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(color)
            Text(value)
                .font(.system(size: 14, weight: .bold))
            Text(label)
                .font(.system(size: 11))
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

struct LogVisitSheet: View {
    let restaurant: Restaurant
    @EnvironmentObject var session: UserSession
    @Environment(\.dismiss) private var dismiss

    @State private var starRating: Int = 0
    @State private var isSubmitting = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                VStack(spacing: 4) {
                    Image(systemName: "mappin.and.ellipse")
                        .font(.system(size: 32))
                        .foregroundColor(.accentColor)
                    Text("How was \(restaurant.name)?")
                        .font(.system(size: 20, weight: .bold))
                        .multilineTextAlignment(.center)
                }
                .padding(.top, 8)

                // Star picker
                VStack(spacing: 8) {
                    Text("Your Rating")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.secondary)

                    HStack(spacing: 10) {
                        ForEach(1...5, id: \.self) { star in
                            Image(
                                systemName: star <= starRating
                                    ? "star.fill" : "star"
                            )
                            .font(.system(size: 36))
                            .foregroundColor(
                                star <= starRating
                                    ? .orange : Color(.quaternaryLabel)
                            )
                            .onTapGesture {
                                withAnimation(.spring(response: 0.25)) {
                                    starRating = star
                                }
                            }
                        }
                    }
                }
                .padding(16)
                .frame(maxWidth: .infinity)
                .background(Color(.secondarySystemGroupedBackground))
                .cornerRadius(14)

                Spacer()

                // Submit
                Button(action: submitVisit) {
                    Group {
                        if isSubmitting {
                            ProgressView().tint(.white)
                        } else {
                            Text("Save Visit")
                                .font(.system(size: 16, weight: .semibold))
                        }
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
                    .background(
                        canSubmit ? Color.accentColor : Color(.systemGray4)
                    )
                    .cornerRadius(12)
                }
                .disabled(!canSubmit)
            }
            .padding(20)
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Log Visit")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
            }
        }
    }

    private var canSubmit: Bool {
        starRating > 0
            && !isSubmitting
    }

    private func submitVisit() {
        isSubmitting = true
        Task {
            await visitApi(
                userId: session.userId ?? "0",
                restaurantId: restaurant.id.uuidString,
                visitRating: starRating,
                mealType: "lunch"
            )
            dismiss()
        }
    }
}
