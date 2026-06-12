# Identity SDK Architecture Diagram

Tài liệu này mô tả cấu trúc thư mục và chức năng của các module bên trong Identity SDK (TypeScript/Browser).
Mục đích: Hỗ trợ AI và Developer hiểu rõ vị trí và trách nhiệm của từng thành phần để review, maintain và refactor an toàn.

## Cấu trúc tổng quan

SDK được tổ chức theo hướng tách bạch giữa tầng thu thập tín hiệu, tầng nghiệp vụ và tầng giao tiếp API. Hai luồng nghiệp vụ chính (IVT và Identity) dùng chung một bộ collectors và cùng nguồn data `JsSignals`.

### 1. Collectors — Thu thập tín hiệu
Các collector là pure async function, thu thập tín hiệu từ browser và trả về partial data. Không có side effect.
* `src/collectors/core/`: Shared state (`sharedData`), hàm `patchClientGroup`, `patchMetaArray`, các utility dùng chung (cookie, hash, detect).
* `src/collectors/device/`: Screen, window size, timezone, navigator info, user agent.
* `src/collectors/fingerprint/`: Canvas fingerprint, WebGL fingerprint, audio fingerprint, font detection.
* `src/collectors/browser/`: Plugin list, storage availability, media devices, speech voices, document info.
* `src/collectors/security/`: Automation/headless detection, consent level, permission query.
* `src/collectors/network/`: WebRTC local/public IP, connection type và downlink.
* `src/collectors/user/`: Behavioral data — mouse, scroll, keystroke, touch, click (luôn đọc live, không cache).
* `src/collectors/application/`: Identity async — localStorage ID, indexedDB ID, cookie ID, clock skew.
* `src/collectors/performance/`: GPU benchmark, per-collector timing tracker.
* `src/collectors/capability/`: Browser capability detection.
* `src/collectors/js.ts`: Orchestrator duy nhất — chạy toàn bộ collector theo thứ tự sync rồi async, patch `sharedData`, fire completion event.

### 2. Business Modules — Nghiệp vụ
* `src/ivt/IvtModule.ts`: Kiểm tra người hay bot (Invalid Traffic) — lấy signals hiện tại và POST lên backend để phân tích human/bot.
* `src/idt/IdtModule.ts`: Định danh người dùng và thiết bị (Identity) — build fingerprint summary (composite, fuzzy, hashed identifiers), POST lên backend để merge/link identity node, lưu `node_id` trả về vào `sessionStorage`.

### 3. API Layer — Giao tiếp HTTP
* `src/api/saveSignals.ts`: Lưu data client lên Cloudflare R2 — POST signals qua `fetch` (thông thường) hoặc `sendBeacon` (unload path).
* `src/api/Identity.ts`: POST identity summary lên Identity endpoint, parse response và trả `node_id`.

### 4. Core & Config
* `src/core.ts`: Điều phối dùng chung cho mọi module nghiệp vụ — `collectAllSignals()` (thu thập thông tin client), `getDatas()` (lấy snapshot), `saveSignalDatasSendBeacon()` (lưu lên Cloudflare R2), `getPerformanceStats()`. `saveSignalDatas()` đã `@deprecated`, dùng `saveSignalDatasSendBeacon` thay thế.
* `src/config.ts`: `sdkConfig` — feature flags (`SdkFeatureFlags`) và `autoRun`.
* `src/types.ts`: Canonical types: `NormalizedPayload`, `JsSignals`, `DCEClient*`, `SdkConfig`, `SdkFeatureFlags`. Interface `DCEClientAdEnvironment` đã được định nghĩa nhưng field `ad_environment` trong `DCEClient` đang comment out (PENDING SPRINT 5).
* `src/index.ts`: Entry point duy nhất — expose `window.TQC_Identity_SKD`, wire modules theo feature flags, khởi động auto-run.

### 5. Các module phụ trợ
* `src/consent/`: `Gatekeeper`, `CALFactory`, region detection — quản lý consent level cho toàn SDK.
* `src/temporaryId/`: Temporary identity sync — propagate ID cross-domain.
* `src/utils/`: Hash utilities (sha256, simhash64, UUIDv4).
* `src/version.ts`: `SDK_VERSION`, `PAYLOAD_VERSION` — inject từ build-time env.


# Identity SDK — Architectural Guidelines & Context cho AI

## 1. Tổng quan dự án

`identity-sdk` là browser-only TypeScript SDK với bốn nhiệm vụ chính:
1. **Thu thập thông tin client**: `collectAllSignals()` chạy toàn bộ collectors (fingerprint, device, behavioral, network...) và lưu snapshot vào RAM.
2. **Lưu data lên Cloudflare R2**: `saveSignalDatasSendBeacon()` POST `NormalizedPayload` lên storage backend (dùng `sendBeacon` để đảm bảo gửi được khi trang đóng). `saveSignalDatas()` đã `@deprecated`.
3. **Kiểm tra người hay bot (Invalid Traffic)**: `IvtSendUserSummary()` gửi các signals lên Invalid Traffic endpoint để backend phân tích human/bot.
4. **Định danh người dùng (Identity)**: `IdtSendUserSummary()` build fingerprint summary và POST lên Identity endpoint để backend merge/link identity node.

Nhiệm vụ 3 và 4 dùng chung bộ collectors và cùng nguồn data `NormalizedPayload` (alias `JsSignals`).

Build chain: TypeScript ES2020 (strict) → Vite library mode → Babel (`@babel/preset-env`, target IE11) → Terser. Output: UMD (`identity-sdk.cjs`) + ESM (`identity-sdk.js`). **Zero runtime dependencies** — bundle phải self-contained.

## 2. Cấu trúc thư mục & trách nhiệm từng tầng

### `src/collectors/` — Tầng thu thập (Collection)

Mỗi collector là một async function thuần: không có tham số bắt buộc, trả về `Partial<DCEClientXxx> | null`, không gọi `patchClientGroup()`, không throw exception. Mọi lỗi nội bộ phải được catch và trả `null`.

`src/collectors/js.ts` là **orchestrator duy nhất**: gọi các collector theo thứ tự (sync trước, async sau), patch `sharedData` qua `patchClientGroup()`, fire `COLLECTION_COMPLETE_EVENT` khi toàn bộ async task settled. Không file nào khác được đóng vai trò này.

`src/collectors/core/` giữ `sharedData` (singleton `NormalizedPayload`), export `patchClientGroup`, `patchMetaArray`, `getSharedData` và các utility dùng chung. Đây là điểm duy nhất được phép đọc/ghi trực tiếp vào `sharedData`.

### `src/idt/`, `src/ivt/` — Tầng nghiệp vụ (Business)

Đọc data qua `getDatas()` từ `src/core.ts`. Không đọc `window.__TQC_IDENTITY_SIGNALS__` hay `getSharedData()` trực tiếp. Hai module này độc lập nhau, không import chéo.

`IvtModule` — kiểm tra người hay bot (Invalid Traffic): lấy signals hiện tại và POST lên backend để phân tích human/bot.

`IdtModule` — định danh người dùng và thiết bị (Identity): chỉ gửi fingerprint summary (composite fingerprint, fuzzy fingerprint, hashed identifiers). Không dump toàn bộ `NormalizedPayload` vào Identity payload. Lưu `node_id` trả về vào `sessionStorage`.

### `src/api/` — Tầng HTTP

Nơi duy nhất được phép chứa URL endpoint và build-time URL constant (`__IVT_URL__`, `__IDT_URL__`). Module nghiệp vụ nhận URL qua constant, không hardcode trực tiếp trong `idt/` hay `ivt/`.

### `src/index.ts` — Entry point

Chỉ wire modules, đọc feature flags, expose `window.TQC_Identity_SKD` và đăng ký auto-run. Không chứa business logic hay collector. Guard `window.__TQC_IDENTITY_INITIALIZED__` để tránh double-init khi script load nhiều lần.

## 3. Quy tắc làm việc & dependency

1. **Giữ đúng chiều phụ thuộc:** `collectors/ → core.ts → idt/ ivt/ → index.ts`. Collector không import từ `idt/`, `ivt/`, `core.ts`. `idt/` và `ivt/` không import nhau. `index.ts` là file duy nhất expose ra `window`.
2. **Collector không tự patch:** Collector trả `Partial<DCEClientXxx> | null`, để `js.ts` gọi `patchClientGroup()`. Không gọi patch bên trong collector.
3. **Signal mới mặc định vào `asyncTasks[]`:** Collector nặng (canvas, WebGL, audio, GPU, WebRTC, font) phải fire-and-forget trong `asyncTasks[]`, không `await` trực tiếp — tránh block page load. Chỉ đưa vào sync phase khi collector rất nhanh và kết quả cần thiết cho bước tiếp theo. Collector có thể treo phải tự có timeout nội bộ — quá giờ trả `null`.
4. **Behavioral data không bao giờ cache:** `getDatas()` gọi `getBehavioralData()` live mỗi lần. Không memoize vào biến module.
5. **Schema `NormalizedPayload` cố định:** 6 group (`device`, `environment`, `network_probes`, `behavioral`, `identity`, `page_context`). Signal mới phải slot vào group có sẵn — không thêm top-level field, không tạo group mới. Primitive dùng `T | null`; array dùng `T[]`; không dùng `undefined`.
6. **Fail-safe toàn bộ SDK:** Mọi browser API phải có feature check + `try/catch` silent, trả `null` khi lỗi. Mọi truy cập storage (`sessionStorage`, `localStorage`, `IndexedDB`, `cookies`) phải trong `try/catch`. Lỗi mạng, lỗi collector đều xử lý silent — không throw, không crash JS trang host.
7. **SDK không được ảnh hưởng trang khách hàng:** Chạy hoàn toàn nền, không block `DOMContentLoaded`/`load`, không chặn main thread, không dùng synchronous XHR. Auto-run chỉ sau khi `readyState` là `complete` hoặc `interactive`. Không làm chậm LCP, FID, CLS của trang host.
8. **URL chỉ trong `src/api/`:** Dùng build-time constant `__IVT_URL__` / `__IDT_URL__`. `sendBeacon` chỉ dùng cho unload path — POST thông thường dùng `fetch`.
9. **Feature flag cho API mới:** Function mới expose ra `TQC_Identity_SKD` phải có flag tương ứng trong `SdkFeatureFlags` (`types.ts`) và `sdkConfig.features` (`config.ts`).
10. **Zero runtime dependencies:** Không thêm package vào `"dependencies"`. Không dùng Node.js API — runtime là browser-only.

## 4. Quy ước đặt tên & tổ chức

- **File:** `camelCase` theo chức năng — `collectCanvasFingerprint`, `collectWebRTCInfo`. Mỗi file collector export một hoặc một nhóm hàm liên quan của cùng signal group.
- **Collector function:** prefix `collect` cho sync/async collector — `collectScreenInfo`, `collectAutomation`. Hàm đọc behavioral không prefix `collect` vì không gọi từ `js.ts` trực tiếp: `getBehavioralData`.
- **Type/Interface trong `types.ts`:** group interface prefix `DCEClient` — `DCEClientDevice`, `DCEClientEnvironment`. Không tạo type ngoài `types.ts` nếu là canonical signal type.
- **Constant:** `UPPER_SNAKE_CASE` — `COLLECTION_COMPLETE_EVENT`, `SDK_VERSION`, `PAYLOAD_VERSION`.
- **Build-time constant:** khai báo `declare const __XYZ__: string` trong file dùng, định nghĩa trong `vite.config.ts`.
- **TypeScript strict:** `strict: true` + `noUnusedLocals` + `noUnusedParameters` đang bật. Không dùng `any` tùy tiện; dùng `unknown` + narrowing khi kiểu chưa rõ. Không dùng non-null assertion `!` không có guard rõ ràng trước đó.

## 5. Nguyên tắc refactor cho AI

- Bảo toàn public API của `window.TQC_Identity_SKD` — không đổi tên hàm, signature hoặc bỏ feature đang enabled nếu chưa có yêu cầu rõ ràng.
- Không thay đổi schema `NormalizedPayload` / `DCEClient*` khi chưa xác nhận ảnh hưởng backend parser.
- Không chuyển async collector sang sync phase và ngược lại khi chưa đo lường performance impact bằng `getPerformanceStats()`.
- Không thêm dependency runtime mới. Không thêm Node.js API vào source — bundle chạy trong browser.
- Giữ nguyên behavior fail-safe: nếu refactor khiến một collector throw thay vì trả `null`, đó là regression.
- Tuân theo pattern của collector cùng nhóm gần nhất khi thêm collector mới; đăng ký đúng vào sync hoặc `asyncTasks[]` trong `js.ts`.
- Ưu tiên thay đổi nhỏ, đúng tầng, dễ review.
