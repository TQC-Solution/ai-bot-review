# PubStar iOS SDK Architecture Diagram

Tài liệu này mô tả cấu trúc thư mục và chức năng của các module bên trong PubStar SDK (ngôn ngữ Swift). 
Mục đích: Hỗ trợ AI và Developer hiểu rõ vị trí và chức năng của từng thành phần để phục vụ việc maintain và refactor.

## Cấu trúc tổng quan

Dự án được chia thành các Adapter mạng quảng cáo (Ad Networks) và phần lõi (Core) của SDK.

### 1. Ad Network Adapters
Các thư mục này chứa mã nguồn để giao tiếp với các mạng quảng cáo bên thứ 3. Mỗi adapter sẽ implement các giao thức (protocols) hoặc kế thừa từ class cơ sở (base) được định nghĩa trong `core`.
* `/AdapterGoogle`: Tích hợp Google Mobile Ads (AdMob/AdManager).
* `/AdapterOrtb`: Tích hợp OpenRTB.
* `/AdapterPrebid`: Tích hợp Prebid Mobile.
* `/AdapterPubStar`: Adapter nội bộ của PubStar.
* `/AdpterAppLovin`: Tích hợp AppLovin MAX.

### 2. Core Module (`/core`)
Thư mục `core` chứa toàn bộ logic vận hành chính của SDK, xử lý giao tiếp giữa ứng dụng (Host App) và các SDK Adapter.
* `/core/api`: Chứa các Public API của SDK được export ra ngoài cho ứng dụng tích hợp gọi đến.
* `/core/adapter`: Chứa logic xử lý, điều phối và giao tiếp chung với các SDK Adapter.
* `/core/base`: Chứa các Base Classes và Protocols nội bộ để các Adapter hoặc tính năng khác kế thừa, đảm bảo tính đa hình.
* `/core/constants`: Lưu trữ các hằng số Global (Config keys, Error codes, v.v.).
* `/core/extensions`: Chứa các Swift Extensions cho các kiểu dữ liệu cơ bản (Dictionary, Array, String, View...).
* `/core/handles`: Chứa các class đóng vai trò là tham số (Parameters/Configurations) của các API được export ra bên ngoài.
* `/core/models`: Định nghĩa các Data Models, Objects sử dụng xuyên suốt bên trong SDK.
* `/core/protocols`: Chứa các protocol listener dùng chung và được export ra ngoài để ứng dụng mobile hứng sự kiện từ SDK (ví dụ: `AdDelegate`, `RewardListener`).
* `/core/services`: Cung cấp các dịch vụ tương tác hệ thống hoặc API bên ngoài (ví dụ: `getIDFA`, `loadAndSaveIp`).
* `/core/task`: Chứa các lớp đảm nhiệm tác vụ Network (giao tiếp với Server), parse JSON response và map vào các `models`.
* `/core/utils`: Các lớp Utility/Helper hỗ trợ xử lý logic chung bên trong SDK.

### 3. Cấu hình & Giao diện (Config & UI)
* `/Enviroments`: Chứa các cấu hình môi trường (Dev, Staging, Prod) khi build SDK ra định dạng XCFramework.
* `/layouts`: Định nghĩa các Custom Views hiển thị quảng cáo (Native Ads, Banner layout) bên trong SDK.
* `/report`: (Dự kiến) Chứa logic tracking, telemetry và gửi báo cáo (analytics) về server.
* `/testmode`: Chứa các cấu hình hoặc mock data để test SDK trên môi trường Sandbox.


# PubStar iOS SDK - Architectural Guidelines & Context cho AI

Dự án PubStar SDK được xây dựng trên Swift, cung cấp giải pháp Mediation/Ad Serving. Hãy đọc kỹ các quy tắc và cấu trúc dưới đây trước khi tiến hành refactor hoặc sinh code.

## 1. Phân tầng Kiến trúc (Layered Architecture)

Hệ thống được chia làm 3 tầng chính, tuân thủ nguyên tắc Dependency Inversion:
1. **Public/Presentation Layer:** Những gì App tích hợp có thể nhìn thấy.
2. **Core Domain Layer:** Logic nghiệp vụ chính của SDK.
3. **Infrastructure/Adapter Layer:** Giao tiếp với mạng quảng cáo bên thứ 3 và Network/System.

## 2. Ranh giới Module & Quy tắc truy cập (Access Control Rules)

### A. Lớp Giao tiếp Công khai (Public Facing)
Bất kỳ file nào nằm trong các thư mục dưới đây **BẮT BUỘC** phải sử dụng access modifier là `public` hoặc `open`. AI không được phép đưa logic xử lý nghiệp vụ phức tạp vào đây.
* `/core/api`: Các endpoint khởi tạo SDK, load ad, show ad.
* `/core/handles`: Các tham số đầu vào (Config objects) mà App truyền vào SDK.
* `/core/protocols`: Các Delegate/Listener (ví dụ: báo callback `onAdLoaded`, `onAdFailedToLoad`).

### B. Lớp Lõi Nghiệp vụ (Core Business Logic - Internal)
Các thư mục này chứa logic nội bộ. Mặc định sử dụng `internal` access modifier. Tuyệt đối không expose các class này ra ngoài SDK.
* `/core/models`: Plain Swift Objects, struct chứa dữ liệu.
* `/core/task`: Lớp chịu trách nhiệm Network request (Gọi API lấy config, bidding, report). Parse JSON thành `models`.
* `/core/services`: Tương tác với hệ điều hành (Get IDFA, Network Info, Location).
* `/core/utils` & `/core/extensions`: Helper functions.
* `/layouts`: Chứa logic render UI cho các format quảng cáo (Native, Banner).

### C. Lớp Adapter & Khả năng Mở rộng (Infrastructure)
* `/core/base`: Khung xương định nghĩa `BaseAdAdapter` class hoặc `AdAdapterProtocol`. 
* `/core/adapter`: Tầng trung gian (Mediation Controller), quyết định sẽ gọi Adapter của mạng quảng cáo nào dựa trên Waterfall hoặc Bidding response.
* **Các Ad Networks (`/AdapterGoogle`, `/AdapterPrebid`, v.v.):** BẮT BUỘC phải kế thừa từ các class trong `/core/base`. Không được phép gọi trực tiếp các module bên ngoài (không cross-dependency giữa các adapter).

## 3. Quy tắc Refactoring cho AI
1. **Bảo toàn Public API:** Khi refactor `/core/api`, tuyệt đối không thay đổi signature của các public function trừ khi được yêu cầu rõ ràng, vì sẽ làm gãy ứng dụng (breaking change) của client đang dùng XCFramework.
2. **SOLID:** Luôn ưu tiên dùng Protocol (`/core/protocols`) để giao tiếp ngược từ Adapter về Core.
3. **Môi trường:** Khi làm việc với logic URL hoặc API Endpoint, phải check cấu hình từ `/Enviroments` hoặc `/testmode`.