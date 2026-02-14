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
        VStack(spacing: 16) {
            Text("Settings")
                .font(.largeTitle)

            Button(
                action: { session.deleteUser() }
            ) {
                Text("Delete User").frame(
                    maxWidth: .infinity,
                    alignment: .center
                )
            }
        }
        .padding()
    }
}
