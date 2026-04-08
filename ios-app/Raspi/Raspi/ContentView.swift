//
//  ContentView.swift
//  Raspi
//
//  Created by Reece Needham on 3/30/26.
//

import SwiftUI
import WebKit

struct ContentView: View {
    
    private let nfcBridge = NFCBridge()

    var body: some View {
        WebView(url: URL(string: "http://raspinonpwa.reecen.dev/")!, nfcBridge: nfcBridge)
            .webViewBackForwardNavigationGestures(.disabled)
            .scrollBounceBehavior(.basedOnSize, axes: [.vertical, .horizontal])
            .webViewLinkPreviews(.disabled)
            .webViewMagnificationGestures(.disabled)
            .ignoresSafeArea(edges: .bottom)
    }
}

#Preview {
    ContentView()
}
