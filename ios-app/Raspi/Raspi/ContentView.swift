//
//  ContentView.swift
//  Raspi
//
//  Created by Reece Needham on 3/30/26.
//

import SwiftUI
import WebKit

struct ContentView: View {
    
    private let webView: WKWebView = {
        let contentController = WKUserContentController()
        let config = WKWebViewConfiguration()
        config.userContentController = contentController
        return WKWebView(frame: .zero, configuration: config)
    }()
    
    private var nfcReader: NFCReader { NFCReader(wv: webView) }

    var body: some View {
        WebView(webView: self.webView, url: URL(string: "http://raspinonpwa.reecen.dev/")!, nfcReader: nfcReader)
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
