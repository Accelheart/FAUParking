//
//  ContentView.swift
//  Parking
//
//  Created by Khalid Abdallah on 11/24/25.
//

import SwiftUI

struct MainTabView: View {
    @StateObject private var spotsViewModel = SpotsViewModel()

    var body: some View {
        TabView {
            DashboardView()
                .environmentObject(spotsViewModel)
                .tabItem {
                    Label("Dashboard", systemImage: "dot.radiowaves.left.and.right")
                }

            SpotsListView()
                .environmentObject(spotsViewModel)
                .tabItem {
                    Label("Spots", systemImage: "parkingsign.circle")
                }

            DronesListView(drones: MockData.drones)
                .tabItem {
                    Label("Drones", systemImage: "airplane.circle")
                }

            AlertsListView(alerts: MockData.alerts)
                .tabItem {
                    Label("Alerts", systemImage: "exclamationmark.triangle")
                }
        }
        .task {
            await spotsViewModel.load()
        }
    }
}

#Preview {
    MainTabView()
}
