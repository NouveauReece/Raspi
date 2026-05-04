//
//  ContentView.swift
//  Raspi
//
//  Created by Reece Needham on 3/30/26.
//

import SwiftUI
import WebKit

struct ContentView: View {

    // Both stored as constants so they're never recreated on body re-evaluation
    private let webView: WKWebView = {
        let config = WKWebViewConfiguration()
        config.userContentController = WKUserContentController()
        return WKWebView(frame: .zero, configuration: config)
    }()

    private let nfcReader: NFCReader

    init() {
        nfcReader = NFCReader(wv: webView)
    }

    var body: some View {
        WebView(webView: webView, url: URL(string: "http://raspinonpwa.reecen.dev/")!, nfcReader: nfcReader)
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
