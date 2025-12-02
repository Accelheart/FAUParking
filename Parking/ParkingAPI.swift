//
//  ParkingAPI.swift
//  Parking
//
//  Created by Khalid Abdallah on 12/2/25.
//

import Foundation

final class ParkingAPI {
    static let shared = ParkingAPI()

    // TODO: change to your actual backend base URL
    // e.g. URL(string: "http://127.0.0.1:8000")! when using a tunnel / local network
    private let baseURL = URL(string: "https://parking.2759359719sw.workers.dev")!

    private let decoder: JSONDecoder

    private init() {
        let d = JSONDecoder()
        d.dateDecodingStrategy = .iso8601
        decoder = d
    }

    private func get<T: Decodable>(_ path: String) async throws -> T {
        let url = baseURL.appendingPathComponent(path)

        let (data, response) = try await URLSession.shared.data(from: url)

        guard let http = response as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }

        return try decoder.decode(T.self, from: data)
    }

    // MARK: - Public API

    func fetchLots() async throws -> [Lot] {
        // expects GET /api/lots → array of Lot JSON objects
        try await get("/api/lot")
    }

    func fetchSpaces() async throws -> [Space] {
        // expects GET /api/spaces → array of Space JSON objects
        try await get("/api/space")
    }
}
