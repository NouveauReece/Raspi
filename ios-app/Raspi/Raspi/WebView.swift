//
//  WebView.swift
//  Raspi
//
//  Created by Reece Needham on 3/30/26.
//

import SwiftUI
import WebKit

struct WebView: UIViewRepresentable {

    let url: URL
    let nfcBridge: NFCBridge

    func makeUIView(context: Context) -> WKWebView {

        let contentController = WKUserContentController()

        // JS → Native
        contentController.add(
            context.coordinator,
            name: "nfcScan"
        )

        let config = WKWebViewConfiguration()
        config.userContentController = contentController

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator

        // Native → JS
        nfcBridge.webView = webView

        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(nfcBridge: nfcBridge)
    }
}

final class Coordinator: NSObject,
                         WKScriptMessageHandler,
                         WKNavigationDelegate {

    let nfcBridge: NFCBridge

    init(nfcBridge: NFCBridge) {
        self.nfcBridge = nfcBridge
    }

    // JavaScript → Native
    func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage
    ) {
        if message.name == "nfcScan" {
            print("Received message 'nfcScan'")
            nfcBridge.startScan()
        }
    }
}
