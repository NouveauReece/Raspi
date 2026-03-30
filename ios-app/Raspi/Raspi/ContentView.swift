//
//  ContentView.swift
//  Raspi
//
//  Created by Reece Needham on 3/30/26.
//

import SwiftUI
import WebKit

struct ContentView: View {
    var body: some View {
        VStack {
            WebView(url: URL(string: "https://www.apple.com")!)
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
