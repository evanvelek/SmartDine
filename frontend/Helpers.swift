//
//  Helpers.swift
//  SmartDine
//
//  Created by Evan Velek on 2/15/26.
//

import Foundation
import SwiftUI

let roundedRatingToImage: [Double: String] = [
    0: "zeroStar",
    0.5: "halfStar",
    1: "oneStar",
    1.5: "oneHalfStar",
    2: "twoStar",
    2.5: "twoHalfStar",
    3: "threeStar",
    3.5: "threeHalfStar",
    4.0: "fourStar",
    4.5: "fourHalfStar",
    5.0: "fiveStar",
]

func recursiveRatingToRoundedRatingUp(rating: Double, steps: Int) -> (
    Double, Int
) {

    if roundedRatingToImage[rating] != nil {
        return (rating, steps)
    }

    return recursiveRatingToRoundedRatingUp(
        rating: rating + 0.1,
        steps: steps + 1
    )
}

func recursiveRatingToRoundedRatingDown(rating: Double, steps: Int) -> (
    Double, Int
) {

    if roundedRatingToImage[rating] != nil {
        return (rating, steps)
    }

    return recursiveRatingToRoundedRatingDown(
        rating: rating - 0.1,
        steps: steps + 1
    )
}

func ratingToRoundedRating(
    rating: Double,
) -> Double {

    if roundedRatingToImage[rating] != nil {
        return rating
    }

    let a1 = recursiveRatingToRoundedRatingUp(rating: rating, steps: 0)
    let a2 = recursiveRatingToRoundedRatingDown(rating: rating, steps: 0)

    if a1.1 <= a2.1 {
        return a1.0
    }
    return a2.0
}

func starImage(index: Int, rating: Double) -> String {
    let i = Double(index)
    if rating >= i + 1 {
        return "star.fill"
    } else if rating >= i + 0.5 {
        return "star.leadinghalf.filled"
    } else {
        return "star"
    }
}

func ratingToStarImage(index: Int, rating: Double) -> String {
    return starImage(index: index, rating: ratingToRoundedRating(rating: rating))
}
