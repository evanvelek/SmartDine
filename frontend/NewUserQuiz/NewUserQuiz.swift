//
//  NewUserQuiz.swift
//  SmartDine
//
//  Created by Evan Velek on 2/9/26.
//

import Foundation
import SwiftUI

enum Allergy: String, CaseIterable, Identifiable {
    case peanuts, dairy, shellfish, gluten, soy, vegetarian, vegan

    var id: String { rawValue }
    var label: String {
        rawValue.capitalized
    }
}

enum Cuisines: String, CaseIterable, Identifiable {
    case american, indian, thai, italian, mexican, french, japanese, korean,
        vietnamese, greek, spanish, mediterranean, chinese

    var id: String { rawValue }

    var emoji: String {
        switch self {
        case .american: "🍔"
        case .indian: "🍛"
        case .thai: "🍜"
        case .italian: "🍝"
        case .mexican: "🌮"
        case .french: "🥖"
        case .japanese: "🍣"
        case .korean: "🥢"
        case .vietnamese: "🍲"
        case .greek: "🥙"
        case .spanish: "🥘"
        case .mediterranean: "🫒"
        case .chinese: "🥡"
        }
    }

    var label: String {
        "\(emoji) \(rawValue.capitalized)"
    }
}

struct QuizOption: Identifiable {
    let id = UUID()
    let title: String
    let imageName: String
    var isEmoji: Bool = true
}

struct QuizQuestion: Identifiable {
    let id = UUID()
    let prompt: String
    let options: [QuizOption]
}

struct NewUserQuiz: View {
    @EnvironmentObject var session: UserSession
    @AppStorage("max_distance_m") var max_distance_m: Int = 2000
    @AppStorage("transport_mode") var transport_mode: String = "walk"

    @State private var selectedAllergies: Set<Allergy> = []
    @State private var selectedCuisines: Set<Cuisines> = []
    @State private var hasSelectedAllergies: Bool = false
    @State private var hasSelectedCuisines: Bool = false

    @State private var currentIndex = 0
    @State private var favoriteDishes: [QuizOption] = []

    @State var QR: QuizResult = QuizResult()

    let questions: [QuizQuestion] = [
        QuizQuestion(
            prompt: "What is your preferred maximum distance?",
            options: [
                QuizOption(title: "2km", imageName: ""),
                QuizOption(title: "10km", imageName: ""),
                QuizOption(title: "20km", imageName: ""),
                QuizOption(title: "100km", imageName: ""),
            ]
        ),
        QuizQuestion(
            prompt: "What is your preferred price range?",
            options: [
                QuizOption(title: "$", imageName: ""),
                QuizOption(title: "$$", imageName: ""),
                QuizOption(title: "$$$", imageName: ""),
                QuizOption(title: "$$$$", imageName: ""),
            ]
        ),
    ]

    let columns = [
        GridItem(.flexible()),
        GridItem(.flexible()),
    ]

    private func select(_ option: QuizOption) {
        favoriteDishes.append(option)
        if currentIndex == 0 {
            if option.title == "10km" {
                QR.maxDistanceM = 10000
                max_distance_m = 10000
            } else if option.title == "20km" {
                QR.maxDistanceM = 20000
                max_distance_m = 20000
            } else if option.title == "100km" {
                QR.maxDistanceM = 100000
                max_distance_m = 100000
            }
        } else if currentIndex == 1 {
            QR.budgetMaxPriceLevel = option.title.count
        }
        if currentIndex < questions.count - 1 {
            currentIndex += 1
        } else {
            QR.preferedCuisines = selectedCuisines.map { $0.rawValue }.joined(
                separator: ","
            )
            Task {
                await session.saveUser(
                    quizData: QR,
                    selectedAllergies: selectedAllergies
                )
            }
        }
    }

    private func finishAllergies() {
        hasSelectedAllergies = true
    }

    private func finishCuisineSelection() {
        hasSelectedCuisines = true
    }

    var body: some View {
        VStack {
            Text("User Preferences")
                .font(.largeTitle)
                .padding()
                .multilineTextAlignment(.center)

            Text(
                "Please answer the following questions to help us tailor your dining experience."
            )
            .padding()
            .multilineTextAlignment(.center)

            switch hasSelectedAllergies {
            case false:
                Form {
                    Section(
                        header: Text(
                            "Which of these dietary restrictions apply to you?"
                        )
                    ) {
                        ForEach(Allergy.allCases) { allergy in
                            Toggle(
                                allergy.label,
                                isOn: Binding(
                                    get: {
                                        selectedAllergies.contains(allergy)
                                    },
                                    set: {
                                        isSelected in
                                        if isSelected {
                                            selectedAllergies.insert(allergy)
                                        } else {
                                            selectedAllergies.remove(allergy)
                                        }
                                    }
                                )
                            )
                        }
                    }
                    Section {
                        Button(
                            action: { finishAllergies() }
                        ) {
                            Text("Next").frame(
                                maxWidth: .infinity,
                                alignment: .center
                            )
                        }
                    }
                }
            case true:
                switch hasSelectedCuisines {
                case false:
                    Form {
                        Section(
                            header: Text(
                                "Please select any number of these cuisines you especially enjoy."
                            )
                        ) {
                            ForEach(Cuisines.allCases) { cuisine in
                                Toggle(
                                    cuisine.label,
                                    isOn: Binding(
                                        get: {
                                            selectedCuisines.contains(cuisine)
                                        },
                                        set: { isSelected in
                                            if isSelected {
                                                selectedCuisines.insert(cuisine)
                                            } else {
                                                selectedCuisines.remove(cuisine)
                                            }
                                        }
                                    )
                                )
                            }
                        }

                        Section {
                            Button(action: finishCuisineSelection) {
                                Text("Next")
                                    .frame(maxWidth: .infinity)
                            }
                        }
                    }
                case true:
                    Form {
                        VStack(spacing: 24) {
                            Text(
                                "Question \(currentIndex + 1) of \(questions.count)"
                            )
                            .font(.subheadline)
                            .foregroundColor(.secondary)

                            Text(questions[currentIndex].prompt)
                                .font(.title2)
                                .multilineTextAlignment(.center)

                            LazyVGrid(columns: columns, spacing: 16) {
                                ForEach(questions[currentIndex].options) {
                                    option in
                                    OptionCard(option: option) {
                                        select(option)
                                    }
                                }
                            }
                            .padding(.top, 12)

                            Spacer()
                        }
                        .padding()
                        .animation(.easeInOut, value: currentIndex)
                    }
                }
            }
        }

    }
}

#Preview {
    NewUserQuiz()
}
