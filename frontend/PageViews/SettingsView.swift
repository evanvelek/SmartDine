//
//  SettingsView.swift
//  SmartDine
//
//  Created by Evan Velek on 2/9/26.
//
import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var session: UserSession

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Settings rows
                List {
                    Section {
                        SettingsRow(
                            icon: "slider.horizontal.3",
                            iconColor: .blue,
                            title: "Change Preferences"
                        ) {
                            session.setShowUserQuiz()
                        }
                    }
                }
                .listStyle(.insetGrouped)

                // Delete button pinned to bottom
                VStack(spacing: 12) {
                    Divider()

                    Button(action: { session.deleteUser() }) {
                        HStack(spacing: 8) {
                            Image(systemName: "trash")
                                .font(.system(size: 15, weight: .semibold))
                            Text("Delete Account")
                                .font(.system(size: 16, weight: .semibold))
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(Color.red)
                        .cornerRadius(12)
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 8)
                }
                .background(Color(.systemGroupedBackground))
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.large)
            .background(Color(.systemGroupedBackground))
        }
    }
}

struct SettingsRow: View {
    let icon: String
    let iconColor: Color
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                RoundedRectangle(cornerRadius: 8)
                    .fill(iconColor)
                    .frame(width: 32, height: 32)
                    .overlay(
                        Image(systemName: icon)
                            .font(.system(size: 15, weight: .medium))
                            .foregroundColor(.white)
                    )

                Text(title)
                    .font(.system(size: 16))
                    .foregroundColor(.primary)

                Spacer()

                Image(systemName: "chevron.right")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(Color(.tertiaryLabel))
            }
            .padding(.vertical, 4)
        }
    }
}
