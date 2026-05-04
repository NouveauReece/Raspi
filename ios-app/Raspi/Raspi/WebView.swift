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

final class Coordinator: NSObject, WKScriptMessageHandler, WKNavigationDelegate {

    let nfcReader: NFCReader

    init(reader: NFCReader) {
        self.nfcReader = reader
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        
        print(message.name)
        print(message.body)
        
        guard message.name == "nfcScan" else { return }

        // Body is a dictionary when JS passes an object, or nil/missing for a plain scan
        if let body = message.body as? [String: Any] {
            if let textToWrite = body["write"] as? String {
                // Optional "type" key: "T" (default, plain text) or "U" (URI)
                let type = body["type"] as? String ?? "T"
                nfcReader.write(text: "HEL\(textToWrite)", type: type)
                print("write")
                return
            }
        }

        Task { [weak self] in 
            guard let self = self else { return }
            await self.nfcReader.read()
        }
        

    }
}
