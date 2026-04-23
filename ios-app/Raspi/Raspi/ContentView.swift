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
    private let nfcReader = NFCReader()

    var body: some View {
        WebView(url: URL(string: "http://raspinonpwa.reecen.dev/")!, nfcBridge: nfcBridge, nfcReader: nfcReader)
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
