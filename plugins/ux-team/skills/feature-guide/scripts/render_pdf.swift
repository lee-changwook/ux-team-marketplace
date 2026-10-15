// PDF 확인: 쪽마다 글자를 출력하고 p1.png… 로 렌더한다.  (feature-guide 스킬)
// usage: swift render_pdf.swift <파일.pdf> <출력 폴더>
// Read 도구가 PDF를 바로 못 여는 환경이 있어 — 이 스크립트로 PNG를 만든 뒤 Read 한다
import PDFKit
import AppKit
let url = URL(fileURLWithPath: CommandLine.arguments[1]); let out = CommandLine.arguments[2]
let doc = PDFDocument(url: url)!
print("pages", doc.pageCount)
for i in 0..<doc.pageCount {
  let p = doc.page(at: i)!
  print("=== PAGE \(i+1)"); print(p.string ?? "")
  let r = p.bounds(for: .mediaBox); let s: CGFloat = 1.3
  let img = NSImage(size: NSSize(width: r.width*s, height: r.height*s))
  img.lockFocus(); NSColor.white.set(); NSRect(x:0,y:0,width:r.width*s,height:r.height*s).fill()
  let ctx = NSGraphicsContext.current!.cgContext; ctx.scaleBy(x: s, y: s); p.draw(with: .mediaBox, to: ctx); img.unlockFocus()
  let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
  try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: "\(out)/p\(i+1).png"))
}
