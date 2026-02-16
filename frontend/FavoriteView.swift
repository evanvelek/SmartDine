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

    var favorites: [Restaurant] {
        session.getUserFavorites()
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
                    }.frame(height: 80)
                }
            }
            .navigationTitle("Favorites")
            .navigationDestination(for: Restaurant.self) { restaurant in
                VStack {
                    Text(restaurant.name).font(.headline)
                    Text(restaurant.explanation).font(.body)
                }
            }
        }
    }
}

#Preview {
    FavoritesView()
}
