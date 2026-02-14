//
//  OptionCard.swift
//  SmartDine
//
//  Created by Evan Velek on 2/9/26.
//

import Foundation
import SwiftUI

struct OptionCard: View {
    let option: QuizOption
    let onSelect: () -> Void

    var body: some View {
        Button(action: onSelect) {
            VStack(spacing: 8) {
                Image(option.imageName)
                    .resizable()
                    .scaledToFit()
                    .frame(height: 80)

                Text(option.title)
                    .font(.headline)
            }
            .padding()
            .frame(maxWidth: .infinity)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color(.systemGray6))
            )
        }
        .buttonStyle(.plain)
    }
}
#Preview {
    OptionCard(option: .init(title: "Test", imageName: ""), onSelect: {})
}
