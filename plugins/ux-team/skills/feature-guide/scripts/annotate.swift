// 캡처 가공: 개인정보 가리기 + 번호 배지 얹기.  (feature-guide 스킬)
// usage: swift annotate.swift <원본.png> <출력.png> <spec.json>
// spec.json = 순서대로 적용할 작업 배열. 좌표는 원본 픽셀, 왼쪽 위 기준
//   {"op":"fill","x":..,"y":..,"w":..,"h":..,"sx":..,"sy":..}   (sx,sy) 픽셀 색으로 칠함 — 글자 바로 옆 배경을 고른다. 또는 "color":"#RRGGBB"
//   {"op":"text","x":..,"cy":..,"size":..,"text":"김하나","bold":false,"color":"#1F2329"}   cy = 글자 세로 중심
//   {"op":"badge","n":1,"cx":..,"cy":..,"r":..}   빨간 원 번호(#FF5226). r ≈ 이미지 폭의 2% (656px → 13, 1604px → 17)
// 배경 샘플은 출력 비트맵에서 읽는다 — 원본에서 읽으면 색공간 차이로 상자 테두리가 보인다(2026-10-01 실측)
import AppKit
import Foundation
let a = CommandLine.arguments
let src = a[1], dst = a[2], spec = a[3]
let ops = try! JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: spec))) as! [[String: Any]]
let input = NSBitmapImageRep(data: try! Data(contentsOf: URL(fileURLWithPath: src)))!
let W = input.pixelsWide, H = input.pixelsHigh
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: W, pixelsHigh: H, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
rep.size = NSSize(width: W, height: H)
let ctx = NSGraphicsContext(bitmapImageRep: rep)!
NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = ctx
input.size = NSSize(width: W, height: H)
input.draw(in: NSRect(x: 0, y: 0, width: W, height: H))
func d(_ o: [String: Any], _ k: String) -> CGFloat { CGFloat((o[k] as! NSNumber).doubleValue) }
func flipY(_ y: CGFloat, _ h: CGFloat) -> CGFloat { CGFloat(H) - y - h }
func hex(_ s: String) -> NSColor { var v: UInt64 = 0; Scanner(string: String(s.dropFirst())).scanHexInt64(&v)
  return NSColor(deviceRed: CGFloat((v>>16)&255)/255, green: CGFloat((v>>8)&255)/255, blue: CGFloat(v&255)/255, alpha: 1) }
for o in ops {
  switch o["op"] as! String {
  case "fill":
    let c: NSColor = (o["color"] as? String).map(hex) ?? { ctx.flushGraphics(); return rep.colorAt(x: Int(d(o,"sx")), y: Int(d(o,"sy")))! }()
    c.setFill(); NSRect(x: d(o,"x"), y: flipY(d(o,"y"), d(o,"h")), width: d(o,"w"), height: d(o,"h")).fill()
  case "text":
    let size = d(o,"size"); let bold = (o["bold"] as? Bool) ?? false
    let font = NSFont(name: bold ? "AppleSDGothicNeo-Bold" : "AppleSDGothicNeo-Regular", size: size)!
    let attrs: [NSAttributedString.Key: Any] = [.font: font, .foregroundColor: hex((o["color"] as? String) ?? "#1F2329")]
    let str = NSAttributedString(string: o["text"] as! String, attributes: attrs)
    let sz = str.size()
    str.draw(at: NSPoint(x: d(o,"x"), y: flipY(d(o,"cy") - sz.height/2, sz.height)))
  case "badge":
    let r = d(o,"r"), cx = d(o,"cx"), cy = CGFloat(H) - d(o,"cy")
    let shadow = NSShadow(); shadow.shadowBlurRadius = r*0.35; shadow.shadowOffset = NSSize(width: 0, height: -r*0.1); shadow.shadowColor = NSColor(white: 0, alpha: 0.25)
    NSGraphicsContext.saveGraphicsState(); shadow.set()
    NSColor.white.setFill(); NSBezierPath(ovalIn: NSRect(x: cx-r*1.15, y: cy-r*1.15, width: r*2.3, height: r*2.3)).fill()
    NSGraphicsContext.restoreGraphicsState()
    hex("#FF5226").setFill(); NSBezierPath(ovalIn: NSRect(x: cx-r, y: cy-r, width: r*2, height: r*2)).fill()
    let font = NSFont.systemFont(ofSize: r*1.2, weight: .bold)
    let str = NSAttributedString(string: "\(o["n"] as! Int)", attributes: [.font: font, .foregroundColor: NSColor.white])
    let sz = str.size(); str.draw(at: NSPoint(x: cx - sz.width/2, y: cy - sz.height/2))
  default: break
  }
}
NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: dst))
