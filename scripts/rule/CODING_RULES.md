# CODING_RULES.md - PubStar iOS SDK

Tài liệu này quy định các tiêu chuẩn viết code cho dự án PubStar iOS SDK bằng ngôn ngữ Swift. Mọi pull request cần tuân thủ các quy tắc này để đảm bảo tính đồng nhất, dễ bảo trì và tối ưu cho các công cụ tự động (như SwiftLint, SonarQube).

---

## 1. Naming Conventions (Quy tắc đặt tên)

* **PascalCase** cho tên `class`, `struct`, `enum`, `protocol`.
* **camelCase** cho tên biến (`variable`), hằng số (`constant`), hàm (`function`).
* **Boolean:** Biến kiểu `Bool` nên được đặt tên như một lời khẳng định, thường sử dụng các tiền tố như `is`, `has`, `should`, `can`.
    ```swift
    // Tốt
    var isReadyToLoadAd: Bool
    var hasUserConsent: Bool

    // Tránh
    var ready: Bool
    ```
* **Không sử dụng tiền tố (Prefix) cho Swift:** Khác với Objective-C (thường dùng tiền tố như `PS`), Swift có hệ thống Module Namespace. Không thêm tiền tố vào tên class/struct trừ khi class đó cần expose riêng cho Objective-C (`@objc(PSAdManager)`).

## 2. Access Control (Kiểm soát truy cập)

Vì PubStar là một SDK, việc kiểm soát những gì app tích hợp có thể nhìn thấy là tối quan trọng để tránh xung đột và lộ logic nội bộ.

* Mặc định mọi class/struct/function nên để là `internal` (không cần viết từ khóa).
* Chỉ sử dụng `public` cho các API mà PubStar SDK muốn cung cấp cho developer bên ngoài sử dụng.
* Chỉ sử dụng `open` nếu muốn cho phép developer bên ngoài kế thừa class hoặc override function đó (hạn chế tối đa để tránh side-effect).
* Sử dụng `private` hoặc `fileprivate` cho các thuộc tính và hàm xử lý logic nội bộ.

## 3. Code Structure & Organization (Tổ chức code)

* **Protocol Conformance:** Không implement trực tiếp các protocol vào định nghĩa chính của class. Hãy sử dụng `extension` để nhóm các hàm của protocol đó lại.
    ```swift
    class AdLoader {
        // Logic chính của loader
    }

    // MARK: - NetworkDelegate
    extension AdLoader: NetworkDelegate {
        // Các hàm của NetworkDelegate
    }
    ```
* **MARK Comments:** Luôn sử dụng `// MARK: - ` để chia nhỏ các vùng code trong một file lớn (Properties, Initialization, Public Methods, Private Methods). Các bot refactor có thể dựa vào đây để sắp xếp lại code.

## 4. Memory Management (Quản lý bộ nhớ)

* Tránh Retain Cycles (Memory Leak) trong closures. Luôn phân tích xem có cần sử dụng `[weak self]` hoặc `[unowned self]` khi gọi closure bất đồng bộ không. Đối với các thao tác mạng, `[weak self]` là lựa chọn an toàn nhất.
    ```swift
    networkManager.fetchAd { [weak self] response in
        guard let self = self else { return }
        self.process(response)
    }
    ```

---

## 5. Error Handling Strategies (Chiến lược xử lý lỗi)

Việc thiết kế API trả về lỗi nhất quán giúp các developer tích hợp SDK dễ dàng handle các tình huống exception. Dưới đây là hai phương pháp được chấp nhận trong dự án, tùy thuộc vào context của API.

### Phương án 1: Sử dụng `throws` (Swift Native Error Handling)
Sử dụng từ khóa `throws` kết hợp với `do-catch`. Đây là cách chuẩn nhất của Swift hiện tại, đặc biệt phù hợp khi kết hợp với `async/await`.

* **Ví dụ:**
    ```swift
    public func initializeSDK(apiKey: String) async throws {
        guard !apiKey.isEmpty else {
            throw PubStarError.invalidAPIKey
        }
        // Logic khởi tạo
    }
    ```

### Phương án 2: Sử dụng `Result<T, Error>` Type
Sử dụng kiểu `Result` cho các API sử dụng mô hình callback (closure) truyền thống.

* **Ví dụ:**
    ```swift
    public func fetchAdToken(completion: @escaping (Result<String, PubStarError>) -> Void) {
        if let token = cachedToken {
            completion(.success(token))
        } else {
            completion(.failure(.tokenGenerationFailed))
        }
    }
    ```

### Bảng so sánh ưu và nhược điểm

| Tiêu chí | Phương án 1 (`throws` & `async/await`) | Phương án 2 (`Result` type với Closure) |
| :--- | :--- | :--- |
| **Ưu điểm** | Code sạch, đọc tuần tự như code đồng bộ. Khuyên dùng bởi Apple cho SDK hiện đại. Tương thích tốt với bot phân tích luồng. | Rõ ràng về mặt kiểu dữ liệu trả về. Tương thích tốt với các dự án cũ chưa áp dụng concurrency mới. |
| **Nhược điểm** | Yêu cầu base iOS target cao hơn (iOS 13+). Khó tương thích ngược với code Objective-C. | Dễ dẫn đến callback hell nếu có nhiều request lồng nhau. |

---

## 6. Code Formatting Standardization (Công cụ chuẩn hóa Code)

Dự án áp dụng các công cụ tự động để đảm bảo code luôn tuân thủ rule trước khi được merge vào nhánh chính thông qua CI/CD.

### Lựa chọn 1: SwiftLint
Công cụ phân tích tĩnh (Static analysis tool). Nó kiểm tra code dựa trên các rule được cấu hình (ví dụ: độ dài dòng, khoảng trắng, unused variables) và báo warning/error khi build.

* **Ví dụ cấu hình (`.swiftlint.yml`):**
    ```yaml
    line_length:
      warning: 120
      error: 150
    force_cast: warning # Cảnh báo khi dùng 'as!'
    ```

### Lựa chọn 2: SwiftFormat
Công cụ tự động sửa lỗi định dạng code (Auto-formatter). Thay vì chỉ cảnh báo, nó tự động chèn/xóa khoảng trắng, căn lề lại code.

* **Ví dụ sử dụng:** Chạy script `swiftformat .` trước mỗi lần commit.

### Bảng so sánh ưu và nhược điểm

| Tiêu chí | Lựa chọn 1 (SwiftLint) | Lựa chọn 2 (SwiftFormat) |
| :--- | :--- | :--- |
| **Ưu điểm** | Có hàng trăm rules chi tiết về logic code. Lý tưởng để tích hợp vào GitHub Actions chặn PR lỗi. | Giải phóng lập trình viên khỏi việc sửa lỗi căn lề lặt vặt. Code luôn đẹp một cách đồng nhất. |
| **Nhược điểm** | Developer phải tự sửa tay các warning (với hầu hết các rule). | Chỉ sửa được vấn đề thẩm mỹ, không phát hiện được lỗi logic hay memory management. |

> **Quy định:** Dự án PubStar SDK khuyến khích sử dụng **cả hai**. SwiftFormat chạy cục bộ ở máy dev để format code, còn SwiftLint gắn trên GitHub Actions CI/CD để check lỗi trước khi merge.