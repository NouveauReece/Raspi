//
//  NFC.swift
//  Raspi
//
//  Created by Reece Needham on 4/23/26.
//

import SwiftUI
import CoreNFC
import WebKit
public import Combine

@available(iOS 15.0, *)
public class NFCReader: NSObject, ObservableObject, NFCNDEFReaderSessionDelegate {

    var webView: WKWebView
    
    @Published public var startAlert = "Hold your iPhone near the tag."
    @Published public var endAlert = ""
    @Published public var msg = "Scan to read or Edit here to write..."
    @Published public var raw =  "Raw Data available after scan."
    
    init(wv: WKWebView) {
        self.webView = wv
    }

    public var session: NFCNDEFReaderSession?
    
    public func read() {
        guard NFCNDEFReaderSession.readingAvailable else {
            print("Error")
            return
        }
        session = NFCNDEFReaderSession(delegate: self, queue: nil, invalidateAfterFirstRead: true)
        session?.alertMessage = self.startAlert
        session?.begin()
    }
    
    public func readerSession(_ session: NFCNDEFReaderSession, didDetectNDEFs messages: [NFCNDEFMessage]) {
        DispatchQueue.main.async {
            self.msg = messages.map {
                $0.records.map {
                    String(decoding: $0.payload, as: UTF8.self)
                }.joined(separator: "\n")
            }.joined(separator: " ")
            
            self.raw = messages.map {
                $0.records.map {
                    "\($0.typeNameFormat) \(String(decoding:$0.type, as: UTF8.self)) \(String(decoding:$0.identifier, as: UTF8.self)) \(String(decoding: $0.payload, as: UTF8.self))"
                }.joined(separator: "\n")
            }.joined(separator: " ")


            session.alertMessage = self.endAlert != "" ? self.endAlert : "Read \(messages.count) NDEF Messages, and \(messages[0].records.count) Records."
            
            let js = "const p = document.createElement('p'); p.innerText = \"\(self.msg)\"; document.body.appendChild(p);"
            
            print("evaluating:\n\(js)")
            
            self.webView.evaluateJavaScript(js) { _, error in
                if let error { print("JS error: \(error)") }
            }
        }
    }
    
    public func readerSessionDidBecomeActive(_ session: NFCNDEFReaderSession) {
    }
    
    public func readerSession(_ session: NFCNDEFReaderSession, didInvalidateWithError error: Error) {
        print("Session did invalidate with error: \(error)")
        self.session = nil
    }
}


public class NFCWriter: NSObject, ObservableObject, NFCNDEFReaderSessionDelegate {
    @Published public var startAlert = "Hold your iPhone near the tag."
    @Published public var endAlert = ""
    @Published public var msg = ""
    @Published public var type = "T"

    public var session: NFCNDEFReaderSession?
    
    public func write() {
        guard NFCNDEFReaderSession.readingAvailable else {
            print("Error")
            return
        }
        session = NFCNDEFReaderSession(delegate: self, queue: nil, invalidateAfterFirstRead: true)
        session?.alertMessage = self.startAlert
        session?.begin()
    }
    
    public func readerSession(_ session: NFCNDEFReaderSession, didDetectNDEFs messages: [NFCNDEFMessage]) {
    }

    public func readerSession(_ session: NFCNDEFReaderSession, didDetect tags: [NFCNDEFTag]) {
        if tags.count > 1 {
            let retryInterval = DispatchTimeInterval.milliseconds(500)
            session.alertMessage = "Detected more than 1 tag. Please try again."
            DispatchQueue.global().asyncAfter(deadline: .now() + retryInterval, execute: {
                session.restartPolling()
            })
            return
        }
        
        let tag = tags.first!
        session.connect(to: tag, completionHandler: { (error: Error?) in
            if nil != error {
                session.alertMessage = "Unable to connect to tag."
                session.invalidate()
                return
            }
            
            tag.queryNDEFStatus(completionHandler: { (ndefStatus: NFCNDEFStatus, capacity: Int, error: Error?) in
                guard error == nil else {
                    session.alertMessage = "Unable to query the status of tag."
                    session.invalidate()
                    return
                }

                switch ndefStatus {
                case .notSupported:
                    session.alertMessage = "Tag is not NDEF compliant."
                    session.invalidate()
                case .readOnly:
                    session.alertMessage = "Read only tag detected."
                    session.invalidate()
                case .readWrite:
                    let payload: NFCNDEFPayload?
                    if self.type == "T" {
                        payload = NFCNDEFPayload.init(
                            format: .nfcWellKnown,
                            type: Data("\(self.type)".utf8),
                            identifier: Data(),
                            payload: Data("\(self.msg)".utf8)
                        )
                    } else {
                        payload = NFCNDEFPayload.wellKnownTypeURIPayload(string: "\(self.msg)")
                    }
                    let message = NFCNDEFMessage(records: [payload].compactMap({ $0 }))
                    tag.writeNDEF(message, completionHandler: { (error: Error?) in
                        if nil != error {
                            session.alertMessage = "Write to tag fail: \(error!)"
                        } else {
                            session.alertMessage = self.endAlert != "" ? self.endAlert : "Write \(self.msg) to tag successful."
                        }
                        session.invalidate()
                    })
                @unknown default:
                    session.alertMessage = "Unknown tag status."
                    session.invalidate()
                }
            })
        })
    }
    
    public func readerSessionDidBecomeActive(_ session: NFCNDEFReaderSession) {
    }

    public func readerSession(_ session: NFCNDEFReaderSession, didInvalidateWithError error: Error) {
        print("Session did invalidate with error: \(error)")
        self.session = nil
    }
}
