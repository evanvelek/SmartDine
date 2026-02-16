//
//  NewUserQuiz.swift
//  SmartDine
//
//  Created by Evan Velek on 2/9/26.
//

import Foundation
import SwiftUI

enum Allergy: String, CaseIterable, Identifiable {
    case peanuts, dairy, shellfish, gluten, soy

    var id: String { rawValue }
    var label: String {
        rawValue.capitalized
    }
}

struct QuizOption: Identifiable {
    let id = UUID()
    let title: String
    let imageName: String
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
    @State private var hasSelectedAllergies: Bool = false

    @State private var currentIndex = 0
    @State private var favoriteDishes: [QuizOption] = []

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
        QuizQuestion(prompt: "Do you prefer walking or driving?", options: [
            QuizOption(title: "Walking", imageName: ""),
            QuizOption(title: "Driving", imageName: ""),
        ]),
        QuizQuestion(
            prompt: "Pick your favorite of these cuisines",
            options: [
                QuizOption(title: "Italian", imageName: "pizza"),
                QuizOption(title: "American", imageName: "burger"),
                QuizOption(title: "Japanese", imageName: "ramen"),
                QuizOption(title: "Mexican", imageName: "tacos"),
            ]
        ),
        QuizQuestion(
            prompt: "What is your preferred price range?",
            options: [
                QuizOption(title: "Low", imageName: "low"),
                QuizOption(title: "Moderate", imageName: "dollar"),
                QuizOption(title: "Pricy", imageName: "twodollar"),
                QuizOption(title: "Expensive", imageName: "threedollar"),
            ]
        ),
        // TODO: Evan -- Add more quiz questions
    ]

    let columns = [
        GridItem(.flexible()),
        GridItem(.flexible()),
    ]

    private func select(_ option: QuizOption) {
        favoriteDishes.append(option)
        if currentIndex == 0 {
            if option.title == "10km" {
                max_distance_m = 10000
            } else if option.title == "20km" {
                max_distance_m = 20000
            } else if option.title == "100km" {
                max_distance_m = 100000
            }
        } else if currentIndex == 1 {
            if option.title == "Driving" {
                transport_mode = "drive"
            }
        }
        if currentIndex < questions.count - 1 {
            currentIndex += 1
        } else {
            session.saveUser(
                with: QuizResult(
                    selectedAllergies: selectedAllergies,
                    quizAnswers: favoriteDishes
                )
            )
            // TODO: Evan -- Implement quiz submission to backend
        }
    }

    private func finishAllergies() {
        hasSelectedAllergies = true
    }

    var body: some View {
        VStack {
            Text("New User Preferences Quiz")
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
                    Section(header: Text("Allergies")) {
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
                            ForEach(questions[currentIndex].options) { option in
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

#Preview {
    NewUserQuiz()
}
