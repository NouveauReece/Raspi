//
//  WebView.swift
//  Raspi
//
//  Created by Reece Needham on 3/30/26.
//

import SwiftUI
import WebKit

struct WebView: UIViewRepresentable {
    
    let webView: WKWebView
    let url: URL
    let nfcReader: NFCReader

    func makeUIView(context: Context) -> WKWebView {
        
        webView.configuration.userContentController.add(context.coordinator, name: "nfcScan")
        webView.navigationDelegate = context.coordinator
        nfcReader.webView = webView
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(reader: nfcReader)
    }
}

final class Coordinator: NSObject,
                         WKScriptMessageHandler,
                         WKNavigationDelegate {

    let nfcReader: NFCReader

    init(reader: NFCReader) {
        self.nfcReader = reader
    }

    // JavaScript → Native
    func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage
    ) {
        if message.name == "nfcScan" {
            print("Received message 'nfcScan'")
//            nfcBridge.startScan()
            nfcReader.read()
        }
    }
}
