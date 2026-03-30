//
//  NFCBridge.swift
//  Raspi
//
//  Created by Reece Needham on 3/30/26.
//

import Foundation
import CoreNFC
import WebKit

final class NFCBridge: NSObject, NFCNDEFReaderSessionDelegate {

    weak var webView: WKWebView?
    private var session: NFCNDEFReaderSession?

    func startScan() {
        guard NFCNDEFReaderSession.readingAvailable else {
            print("NFC not available")
            return
        }

        session = NFCNDEFReaderSession(
            delegate: self,
            queue: nil,
            invalidateAfterFirstRead: true
        )
        session?.alertMessage = "Hold your iPhone near the Record Player"
        session?.begin()
    }

    func readerSession(
        _ session: NFCNDEFReaderSession,
        didDetectNDEFs messages: [NFCNDEFMessage]
    ) {
        guard
            let record = messages.first?.records.first,
            let payload = String(data: record.payload, encoding: .utf8)
        else { return }

        let escaped = payload
            .replacingOccurrences(of: "\\", with: "\\\\")
            .replacingOccurrences(of: "'", with: "\\'")

        DispatchQueue.main.async {
            self.webView?.evaluateJavaScript(
                "window.onNFCRead && window.onNFCRead('\(escaped)');"
            )
        }
    }

    func readerSession(_ session: NFCNDEFReaderSession,
                       didInvalidateWithError error: Error) {
        print("NFC error:", error)
        self.session = nil
    }
}
