//
//  FavoriteView.swift
//  SmartDine
//
//  Created by Evan Velek on 2/9/26.
//
import Foundation
import SwiftUI

struct FavoritesView: View {
    @EnvironmentObject var session: UserSession
 
    @State private var favorites: [ApiFavorite] = []
    @State private var isLoading = true
    @State private var errorMessage: String? = nil
 
    var body: some View {
        Group {
            if isLoading {
                VStack(spacing: 12) {
                    ProgressView()
                    Text("Loading favorites…")
                        .font(.system(size: 14))
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let error = errorMessage {
                ContentUnavailableView(
                    "Something went wrong",
                    systemImage: "exclamationmark.triangle",
                    description: Text(error)
                )
            } else if favorites.isEmpty {
                ContentUnavailableView(
                    "No Favorites Yet",
                    systemImage: "heart.slash",
                    description: Text("Tap the heart on any restaurant to save it here.")
                )
            } else {
                List {
                    ForEach(favorites, id: \.id) { favorite in
                        NavigationLink(value: favorite) {
                            FavoriteRow(favorite: favorite)
                        }
                    }
                }
                .listStyle(.insetGrouped)
            }
        }
        .navigationTitle("Favorites")
        .navigationBarTitleDisplayMode(.large)
        .task { await loadFavorites() }
        .refreshable { await loadFavorites() }
    }
 
    private func loadFavorites() async {
        guard let userId = session.userId else {
            isLoading = false
            return
        }
        isLoading = favorites.isEmpty  // only show full-screen spinner on first load
        let result = await getFavoritesApi(userId: userId)
        favorites = result.favorites
        isLoading = false
    }
 
}
 
private struct FavoriteRow: View {
    let favorite: ApiFavorite
 
    var body: some View {
        HStack(spacing: 14) {
            RoundedRectangle(cornerRadius: 10)
                .fill(Color(.secondarySystemGroupedBackground))
                .frame(width: 56, height: 56)
                .overlay(
                    Image(systemName: "fork.knife")
                        .font(.system(size: 22, weight: .light))
                        .foregroundColor(Color(.tertiaryLabel))
                )
 
            VStack(alignment: .leading, spacing: 4) {
                Text(favorite.name ?? "Unknown Restaurant")
                    .font(.system(size: 16, weight: .semibold))
                    .lineLimit(1)
 
                if let address = favorite.address, !address.isEmpty {
                    Text(address)
                        .font(.system(size: 13))
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
 
                if let rating = favorite.rating {
                    HStack(spacing: 3) {
                        Image(systemName: "star.fill")
                            .font(.system(size: 11))
                            .foregroundColor(.yellow)
                        Text(String(format: "%.1f", rating))
                            .font(.system(size: 13, weight: .medium))
                    }
                }
            }
 
            Spacer()
 
            Image(systemName: "heart.fill")
                .font(.system(size: 16))
                .foregroundColor(.red)
        }
        .padding(.vertical, 4)
        
    }
}

struct FavoriteDetailView: View {
    let favorite: ApiFavorite
    @EnvironmentObject var session: UserSession

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {

                RoundedRectangle(cornerRadius: 16)
                    .fill(Color(.secondarySystemGroupedBackground))
                    .frame(height: 180)
                    .overlay(
                        Image(systemName: "fork.knife")
                            .font(.system(size: 48, weight: .light))
                            .foregroundColor(Color(.tertiaryLabel))
                    )
                    .padding(.horizontal, 16)
                    .padding(.top, 12)

                HStack(spacing: 12) {
                    Text(favorite.name ?? "Unknown Restaurant")
                        .font(.system(size: 24, weight: .bold))
                }
                .padding(.horizontal, 16)
                .padding(.top, 16)

                HStack(spacing: 0) {
                    if let rating = favorite.rating {
                        StatTile(
                            icon: "star.fill",
                            value: String(format: "%.1f", rating),
                            label: "Rating",
                            color: .yellow
                        )
                    }
                }
                .padding(.vertical, 14)
                .background(Color(.secondarySystemGroupedBackground))
                .cornerRadius(14)
                .padding(.horizontal, 16)
                .padding(.top, 16)

                // Description
                if let description = favorite.description, !description.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(description)
                            .font(.system(size: 15))
                            .foregroundColor(.primary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .padding(14)
                    .background(Color(.secondarySystemGroupedBackground))
                    .cornerRadius(14)
                    .padding(.horizontal, 16)
                    .padding(.top, 16)
                }

                Spacer().frame(height: 32)
            }
        }
        .navigationTitle(favorite.name ?? "Restaurant")
        .navigationBarTitleDisplayMode(.inline)
        .background(Color(.systemGroupedBackground))
    }
}
