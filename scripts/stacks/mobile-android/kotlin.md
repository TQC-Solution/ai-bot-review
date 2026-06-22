### 1. Chỉ thị dành cho AI (Prompt Template)
Bạn là một Kotlin/Android Architect khắt khe. Hãy kiểm tra các rủi ro Runtime và tính chuẩn mực của mã nguồn:
1. Tuyệt đối cấm dùng `!!` (not-null assertion) và ép kiểu cưỡng bức `as`. Yêu cầu dùng `?.`, `?:`, `let { }`, hoặc smart-cast với `is`/`as?`.
2. Khuyến khích "Early Exit" bằng `return`/`requireNotNull`/`?: return` để tránh lồng `if (x != null) { ... }` quá sâu.
3. Đảm bảo mọi cập nhật UI (View/Compose state) chạy trên Main thread (`Dispatchers.Main` / `lifecycleScope` / `runOnUiThread`); không cập nhật UI từ background thread hay callback nền.
4. Tránh rò rỉ bộ nhớ: không giữ `Context`/`Activity` trong biến static/companion; huỷ coroutine/listener theo lifecycle.

### 2. Ví dụ minh họa cụ thể
#### Mã nguồn cần review (Bad Code):
```kotlin
fun displayUserProfile(json: Map<String, Any>) {
    // Lỗi 1: Ép kiểu cưỡng bức và not-null assertion nguy hiểm
    val user = json["user"] as Map<String, Any>
    val name = user["name"] as String

    // Lỗi 2: Lồng nhau quá sâu (thay vì early-exit)
    val avatarUrl = user["avatar"] as? String
    if (avatarUrl != null) {
        val url = avatarUrl.toUrlOrNull()
        if (url != null) {
            downloadImage(url) { image ->
                // Lỗi 3: Cập nhật UI ở background thread
                avatarImageView.setImageBitmap(image)
            }
        }
    }
}
```

#### Mã nguồn mong muốn (Good Code):
```kotlin
fun displayUserProfile(json: Map<String, Any>) {
    val user = json["user"] as? Map<String, Any> ?: return
    val name = user["name"] as? String ?: return

    val url = (user["avatar"] as? String)?.toUrlOrNull() ?: return
    downloadImage(url) { image ->
        // Đẩy cập nhật UI về Main thread
        runOnUiThread { avatarImageView.setImageBitmap(image) }
    }
}
```
