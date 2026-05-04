//
//  NFC.swift
//  Raspi
//
//  Created by Reece Needham on 4/23/26.
//

import SwiftUI
import CoreNFC
import CoreExtendedNFC
import WebKit
import Combine

@available(iOS 13.0, *)
public class NFCReader: NSObject, ObservableObject, NFCTagReaderSessionDelegate {

    var webView: WKWebView

    @Published public var msg = "Scan to read or Edit here to write..."
    @Published public var raw = "Raw Data available after scan."

    public var session: NFCTagReaderSession?

    public init(wv: WKWebView) {
        self.webView = wv
    }

    // MARK: - Read (all tag types)

    public func read() async {
        do {
            let (info, dump) = try await CoreExtendedNFC.scanAndDump()
            
            if let ndefData = dump.parsedNDEFMessage {
                for record in ndefData.records {
                    // Text record
                    if record.typeNameFormat == .wellKnown,
                       record.type == Data([0x54]),
                       record.payload.count > 1 {
                        let statusByte = record.payload[0]
                        let langLength = Int(statusByte & 0x3F)
                        let textStart = 1 + langLength
                        if textStart < record.payload.count,
                           let text = String(data: record.payload[textStart...], encoding: .utf8) {
                            print("Text:", text)
                        }
                    }

                    // URI record
//                    print(record.type)
//                    print(record.typeNameFormat)
//                    print(record.displayType)
                    
                    if record.typeNameFormat == .wellKnown,
                       record.type == Data([0x55]),
                       !record.payload.isEmpty {
                        print("URI:", record.payload)
                    }
                }
            } else {
                // Help debug if NDEF parsing failed
                print("Block count:", dump.blocks.count)
                let raw = dump.blocks.map(\.data).reduce(Data(), +)
//                print("Raw hex:", raw.map { String(format: "%02X", $0) }.joined(separator: " "))
            }

        } catch {
            print("An error occurred: \(error)")
        }
    }

    // MARK: - NFCTagReaderSessionDelegate

    public func tagReaderSessionDidBecomeActive(_ session: NFCTagReaderSession) {}

    public func tagReaderSession(_ session: NFCTagReaderSession, didInvalidateWithError error: Error) {
        print("Session invalidated: \(error)")
        self.session = nil
    }

    public func tagReaderSession(_ session: NFCTagReaderSession, didDetect tags: [NFCTag]) {
        guard tags.count == 1 else {
            session.alertMessage = "Multiple tags detected. Please try again."
            DispatchQueue.global().asyncAfter(deadline: .now() + 0.5) { session.restartPolling() }
            return
        }

        let tag = tags.first!

            // Write
            if pendingWrite != nil {
                session.connect(to: tag) { [weak self] error in
                    guard let self else { return }
                    if let error {
                        self.finishError(session: session, error: "Connection failed: \(error.localizedDescription)")
                        return
                    }
                    guard let ndefTag = tag.asNDEF else {
                        self.finishError(session: session, error: "Tag does not support NDEF writing.")
                        return
                    }
                    self.handleWrite(ndefTag: ndefTag, session: session)
                }
                return
            }

            // Read
            session.connect(to: tag) { [weak self] error in
                
            guard let self else { return }
            if let error {
                session.invalidate(errorMessage: "Connection failed: \(error.localizedDescription)")
                return
            }

            switch tag {

            case .iso7816(let t):
                // Attempt to also read NDEF from this tag
                t.queryNDEFStatus { status, _, error in
                    if status == .readWrite || status == .readOnly {
                        t.readNDEF { message, error in
                            if let message {
                                let ndef = self.parseNDEF(message)
                                self.finish(session: session,
                                            msg: "ISO7816 | AID: \(t.initialSelectedAID)\nNDEF: \(ndef.msg)",
                                            raw: "ISO7816 \(self.hex(t.identifier)) AID:\(t.initialSelectedAID)\n\(ndef.raw)")
                            } else {
                                self.finish(session: session,
                                            msg: "ISO7816 | UID: \(self.hex(t.identifier)) | AID: \(t.initialSelectedAID)",
                                            raw: "ISO7816 \(self.hex(t.identifier)) \(t.initialSelectedAID)")
                            }
                        }
                    } else {
                        self.finish(session: session,
                                    msg: "ISO7816 | UID: \(self.hex(t.identifier)) | AID: \(t.initialSelectedAID)",
                                    raw: "ISO7816 \(self.hex(t.identifier)) \(t.initialSelectedAID)")
                    }
                }

            case .iso15693(let t):
                let uid = self.hex(t.identifier)
                t.readSingleBlock(requestFlags: [.highDataRate, .address], blockNumber: 0) { result in
                    let block0: String
                    switch result {
                    case .success(let data): block0 = self.hex(data)
                    case .failure:           block0 = "n/a"
                    }
                    self.finish(session: session,
                                msg: "ISO15693 | UID: \(uid) | Mfr: \(t.icManufacturerCode) | Block0: \(block0)",
                                raw: "ISO15693 \(uid) mfr:\(t.icManufacturerCode) block0:\(block0)")
                }

            case .miFare(let t):
                let uid = self.hex(t.identifier)
                let family: String
                switch t.mifareFamily {
                case .ultralight: family = "Ultralight"
                case .plus:       family = "Plus"
                case .desfire:    family = "DESFire"
                default:          family = "Unknown"
                }

                if t.mifareFamily == .ultralight {
                    // First read the capability container (page 3) to identify NTAG subtype
                    t.sendMiFareCommand(commandPacket: Data([0x30, 0x03])) { [weak self] data, error in
                        guard let self else { return }

                        if let error {
                            self.finish(session: session,
                                        msg: "MIFARE \(family) | UID: \(uid) | CC read error: \(error.localizedDescription)",
                                        raw: "MIFARE \(family) \(uid) error:\(error)")
                            return
                        }

                        let tagType: String
                        let totalPages: Int
                        if data.count >= 3 {
                            switch data[2] {
                            case 0x12: tagType = "NTAG213"; totalPages = 45
                            case 0x3E: tagType = "NTAG215"; totalPages = 135
                            case 0x6D: tagType = "NTAG216"; totalPages = 231
                            default:
                                tagType = "Ultralight (CC: \(String(format: "%02X", data[2])))"
                                totalPages = 16
                            }
                        } else {
                            tagType = "Ultralight"
                            totalPages = 16
                        }

                        // Read all pages, then check for NDEF on top
                        self.readAllPages(tag: t,
                                          currentPage: 0,
                                          totalPages: totalPages,
                                          accumulated: Data()) { allData in
                            t.queryNDEFStatus { status, _, _ in
                                if status == .readWrite || status == .readOnly {
                                    t.readNDEF { message, _ in
                                        let hex = allData.map { String(format: "%02X", $0) }.joined(separator: " ")
                                        if let message {
                                            let ndef = self.parseNDEF(message)
                                            self.finish(session: session,
                                                        msg: "\(tagType) | UID: \(uid) | \(totalPages) pages\nNDEF: \(ndef.msg)",
                                                        raw: "\(tagType) \(uid) pages:\(totalPages) data:\(hex)\n\(ndef.raw)")
                                        } else {
                                            self.finish(session: session,
                                                        msg: "\(tagType) | UID: \(uid) | \(totalPages) pages",
                                                        raw: "\(tagType) \(uid) pages:\(totalPages) data:\(hex)")
                                        }
                                    }
                                } else {
                                    let hex = allData.map { String(format: "%02X", $0) }.joined(separator: " ")
                                    self.finish(session: session,
                                                msg: "\(tagType) | UID: \(uid) | \(totalPages) pages",
                                                raw: "\(tagType) \(uid) pages:\(totalPages) data:\(hex)")
                                }
                            }
                        }
                    }
                } else {
                    self.finish(session: session,
                                msg: "MIFARE \(family) | UID: \(uid)",
                                raw: "MIFARE \(family) \(uid)")
                }

            case .feliCa(let t):
                let idm = t.currentIDm.map { String(format: "%02X", $0) }.joined()
                let sc  = t.currentSystemCode.map { String(format: "%02X", $0) }.joined()
                self.finish(session: session,
                            msg: "FeliCa | IDm: \(idm) | System Code: \(sc)",
                            raw: "FeliCa idm:\(idm) sc:\(sc)")

            @unknown default:
                session.invalidate(errorMessage: "Unsupported tag type.")
            }
        }
    }
    
    
    private func readAllPages(tag: NFCMiFareTag, currentPage: Int, totalPages: Int, accumulated: Data, completion: @escaping (Data) -> Void) {
        guard currentPage < totalPages else {
            completion(accumulated)
            return
        }

        let readCmd = Data([0x30, UInt8(currentPage)])
        tag.sendMiFareCommand(commandPacket: readCmd) { [weak self] data, error in
            guard let self else { return }

            if let _ = error {
                // Hit the end of readable memory — return what we have
                completion(accumulated)
                return
            }

            let remaining = totalPages - currentPage
            let bytesToKeep = min(4, remaining) * 4
            let newData = accumulated + data.prefix(bytesToKeep)

            self.readAllPages(tag: tag,
                              currentPage: currentPage + 4,
                              totalPages: totalPages,
                              accumulated: newData,
                              completion: completion)
        }
    }

    // MARK: - Write

    public func write(text: String, type: String = "T") {
        guard NFCTagReaderSession.readingAvailable else { return }
        // Store write params, reuse the same session infrastructure
        pendingWrite = (text, type)
        session = NFCTagReaderSession(pollingOption: [.iso14443, .iso15693], delegate: self)
        session?.alertMessage = "Hold your iPhone near the tag to write."
        session?.begin()
    }

    private var pendingWrite: (text: String, type: String)?

    // Intercept didDetect for write mode
    // (called automatically — pendingWrite signals we're in write mode)
    private func handleWrite(ndefTag: NFCNDEFTag, session: NFCTagReaderSession) {
        guard let (text, type) = pendingWrite else { return }
        ndefTag.queryNDEFStatus { status, _, error in
            guard error == nil, status == .readWrite else {
                self.finishError(session: session, error: "Tag is not writable.")
                return
            }
            let payload: NFCNDEFPayload? = type == "U"
                ? NFCNDEFPayload.wellKnownTypeURIPayload(string: text)
                : NFCNDEFPayload(format: .nfcWellKnown,
                                 type: Data("T".utf8),
                                 identifier: Data(),
                                 payload: Data(text.utf8))
            guard let payload else {
                self.finishError(session: session, error: "Could not create NDEF payload.")
                return
            }
            ndefTag.writeNDEF(NFCNDEFMessage(records: [payload])) { error in
                self.pendingWrite = nil
                if let error {
                    self.finishError(session: session, error: "Write failed: \(error.localizedDescription)")
                } else {
                    // Fire success event back to JS
                    DispatchQueue.main.async {
                        let escaped = text
                            .replacingOccurrences(of: "\\", with: "\\\\")
                            .replacingOccurrences(of: "\"", with: "\\\"")
                        let js = "window.dispatchEvent(new CustomEvent('nfcWriteSuccess', { detail: \"\(escaped)\" }))"
                        self.webView.evaluateJavaScript(js) { _, err in
                            if let err { print("JS error: \(err)") }
                        }
                    }
                    session.alertMessage = "Written successfully."
                    session.invalidate()
                }
            }
        }
    }

    // MARK: - Helpers

    private func finish(session: NFCTagReaderSession, msg: String, raw: String) {
        DispatchQueue.main.async {
            self.msg = msg
            self.raw = raw
            let escaped = msg
                .replacingOccurrences(of: "\\", with: "\\\\")
                .replacingOccurrences(of: "\"", with: "\\\"")
            let js = "window.dispatchEvent(new CustomEvent('nfcDidScan', { detail: \"\(escaped)\" }))"
            self.webView.evaluateJavaScript(js) { _, err in
                if let err { print("JS error: \(err)") }
            }
        }
        session.alertMessage = "Tag read successfully."
        session.invalidate()
    }

    private func hex(_ data: Data) -> String {
        data.map { String(format: "%02X", $0) }.joined(separator: ":")
    }

    private func parseNDEF(_ message: NFCNDEFMessage) -> (msg: String, raw: String) {
        let msg = message.records.map {
            String(decoding: $0.payload, as: UTF8.self)
        }.joined(separator: "\n")

        let raw = message.records.map {
            "\($0.typeNameFormat) \(String(decoding: $0.type, as: UTF8.self)) \(String(decoding: $0.payload, as: UTF8.self))"
        }.joined(separator: "\n")

        return (msg, raw)
    }


    private func finishError(session: NFCTagReaderSession, error: String) {
        DispatchQueue.main.async {
            let escaped = error
                .replacingOccurrences(of: "\\", with: "\\\\")
                .replacingOccurrences(of: "\"", with: "\\\"")
            let js = "window.dispatchEvent(new CustomEvent('nfcWriteError', { detail: \"\(escaped)\" }))"
            self.webView.evaluateJavaScript(js) { _, err in
                if let err { print("JS error: \(err)") }
            }
        }
        session.invalidate(errorMessage: error)
        pendingWrite = nil
    }
}

private extension NFCTag {
    var asNDEF: NFCNDEFTag? {
        switch self {
        case .iso7816(let t):  return t
        case .miFare(let t):   return t
        case .iso15693(let t): return t
        case .feliCa(let t):   return t
        @unknown default:      return nil
        }
    }
}


