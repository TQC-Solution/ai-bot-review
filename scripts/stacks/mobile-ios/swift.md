### 1. Chỉ thị dành cho AI (Prompt Template)
Bạn là một Swift Architect khắt khe. Hãy kiểm tra các rủi ro Runtime và tính chuẩn mực của mã nguồn:
1. Tuyệt đối cấm sử dụng Forced Unwrapping (`!`) và Forced Downcasting (`as!`). Yêu cầu sử dụng `if let` hoặc `guard let`.
2. Khuyến khích sử dụng `guard let` cho luồng "Early Exit" để tránh lỗi "Pyramid of Doom" (nested `if let` quá sâu).
3. Đảm bảo mọi tác vụ cập nhật giao diện (UI updates) nằm trong các block bất đồng bộ hoặc callback từ background đều được đẩy về Main Thread (thông qua `DispatchQueue.main.async` hoặc đánh dấu `@MainActor`).

### 2. Ví dụ minh họa cụ thể
#### Mã nguồn cần review (Bad Code):
```swift
func displayUserProfile(from json: [String: Any]) {
    // Lỗi 1: Ép kiểu cưỡng bức và unwrap nguy hiểm
    let user = json["user"] as! [String: Any]
    let name = user["name"] as! String
    
    // Lỗi 2: Pyramid of Doom (Code lồng nhau quá sâu)
    if let avatarUrl = user["avatar"] as? String {
        if let url = URL(string: avatarUrl) {
            downloadImage(from: url) { image in
                // Lỗi 3: Cập nhật UI ở background thread
                self.avatarImageView.image = image
            }
        }
    }
}
```