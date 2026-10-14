# Identity SDK (TypeScript, browser) — Kiến trúc & luật review

Tài liệu mô tả cấu trúc, quy ước và luật review của `identity-sdk`. Căn cứ: 📐 Coding Standards — CORE + TypeScript (CORE §3) + nguyên tắc SDK §1.
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.

## 1. Tổng quan
SDK chỉ chạy trên trình duyệt, bốn nhiệm vụ:
1. Thu thập thông tin client: `collectAllSignals()` chạy toàn bộ collector, lưu snapshot vào RAM.
2. Lưu data lên Cloudflare R2: `saveSignalDatasSendBeacon()` POST `NormalizedPayload` (`sendBeacon` cho unload). `saveSignalDatas()` đã `@deprecated`.
3. IVT: `IvtSendUserSummary()` gửi signals lên Invalid Traffic endpoint.
4. Identity: `IdtSendUserSummary()` gửi fingerprint summary lên Identity endpoint, lưu `node_id` vào `sessionStorage`.
Build: TypeScript ES2020 strict (`noUnusedLocals`, `noUnusedParameters`) → Vite library mode → Babel (`@babel/preset-env`, target IE11) → Terser. Output UMD + ESM. **Zero runtime dependencies.**

## 2. Cấu trúc thư mục & trách nhiệm
- `src/collectors/`: mỗi collector là async function thuần, không tham số bắt buộc, trả `Partial<DCEClientXxx> | null`, không throw, không tự patch. Nhóm: `core/` (`sharedData` singleton, `patchClientGroup`, `patchMetaArray`, `getSharedData`, utility), `device/`, `fingerprint/`, `browser/`, `security/`, `network/`, `user/` (behavioral, luôn đọc live), `application/`, `performance/`, `capability/`.
- `src/collectors/js.ts`: orchestrator DUY NHẤT — chạy collector sync rồi async (`asyncTasks[]`), patch `sharedData`, fire `COLLECTION_COMPLETE_EVENT`.
- `src/core.ts`: `collectAllSignals()`, `getDatas()`, `saveSignalDatasSendBeacon()`, `getPerformanceStats()`.
- `src/ivt/IvtModule.ts`, `src/idt/IdtModule.ts`: nghiệp vụ, đọc data qua `getDatas()`.
- `src/api/`: nơi DUY NHẤT chứa URL/build-time constant (`__IVT_URL__`, `__IDT_URL__`); `saveSignals.ts`, `Identity.ts`.
- `src/config.ts` (`sdkConfig`, feature flag, `autoRun`), `src/types.ts` (`NormalizedPayload`, `JsSignals`, `DCEClient*`, `SdkConfig`, `SdkFeatureFlags`), `src/index.ts` (entry, expose `window.TQC_Identity_SKD`, guard `window.__TQC_IDENTITY_INITIALIZED__`).
- `src/consent/` (`Gatekeeper`, `CALFactory`, region), `src/temporaryId/`, `src/utils/` (sha256, simhash64, UUIDv4), `src/version.ts`.

## 3. Luật review

### 3.1. Chiều phụ thuộc — `collectors → core.ts → idt/ ivt → index.ts`
- [chặn merge] Collector import `idt/`, `ivt/`, `core.ts`; `idt/` và `ivt/` import lẫn nhau; file khác ngoài `index.ts` gán lên `window`.
- [chặn merge] Collector tự gọi `patchClientGroup()`; file khác ngoài `collectors/core/` đọc/ghi trực tiếp `sharedData`; file khác ngoài `js.ts` đóng vai trò orchestrator.
- [cảnh báo] `idt/`/`ivt/` đọc `window.__TQC_IDENTITY_SIGNALS__` hoặc `getSharedData()` thay vì `getDatas()`.
- [cảnh báo] URL endpoint xuất hiện ngoài `src/api/`.

### 3.2. Fail-safe & hiệu năng trang host
- [chặn merge] Collector/API mới có thể throw: browser API không feature-check, storage (`sessionStorage`, `localStorage`, `IndexedDB`, cookie) không try/catch, lỗi mạng không bắt. Collector lỗi phải trả `null`.
- [chặn merge] Chặn main thread hoặc page load: `await` collector nặng (canvas, WebGL, audio, GPU, WebRTC, font) ở phase sync thay vì `asyncTasks[]`; synchronous XHR; auto-run trước khi `readyState` là `interactive`/`complete`.
- [cảnh báo] Collector có thể treo (WebRTC, permission, media devices) không có timeout nội bộ trả `null`.
- [cảnh báo] Cache/memoize behavioral data vào biến module (phải đọc live qua `getBehavioralData()`).
- [cảnh báo] Dùng `sendBeacon` cho POST thường (chỉ dùng cho unload path); dùng `saveSignalDatas()` deprecated trong code mới.

### 3.3. Schema & public API
- [chặn merge] Thêm top-level field hoặc group mới vào `NormalizedPayload` (6 group cố định: `device`, `environment`, `network_probes`, `behavioral`, `identity`, `page_context`).
- [chặn merge] Đổi tên/signature hoặc bỏ hàm public của `window.TQC_Identity_SKD` mà PR không ghi là breaking change.
- [cảnh báo] Đổi schema `NormalizedPayload`/`DCEClient*` mà PR không nêu đã phối hợp backend parser.
- [cảnh báo] Field mới dùng `undefined`/optional thay vì `T | null` (primitive) hoặc `T[]` (array).
- [cảnh báo] Hàm mới expose ra `TQC_Identity_SKD` không có flag trong `SdkFeatureFlags` (`types.ts`) và `sdkConfig.features` (`config.ts`).
- [cảnh báo] `IdtModule` gửi toàn bộ `NormalizedPayload` thay vì fingerprint summary.

### 3.4. Dependency, bảo mật, TypeScript
- [chặn merge] Thêm package vào `dependencies`; dùng Node.js API trong `src/`.
- [chặn merge] Gửi/log raw PII thay vì hash; consent level không được kiểm tra trước khi thu thập/gửi signal cần consent — CHỈ khi diff cho thấy rõ bỏ qua `Gatekeeper`.
- [cảnh báo] Canonical signal type khai báo ngoài `types.ts`; build-time constant không `declare const __XYZ__: string` hoặc không định nghĩa trong `vite.config.ts`.

## 4. Quy ước đặt tên
- [nit] File collector camelCase theo chức năng; hàm collector prefix `collect` (trừ `getBehavioralData`); interface group prefix `DCEClient`; constant `UPPER_SNAKE_CASE`.

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- `saveSignalDatas()` còn trong code (đã `@deprecated`).
- `DCEClientAdEnvironment` đã định nghĩa nhưng field `ad_environment` trong `DCEClient` đang comment out (PENDING SPRINT 5).
- Tên namespace `TQC_Identity_SKD` (chính tả) là public API, KHÔNG đề xuất đổi tên.

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Collector mới theo pattern collector cùng nhóm gần nhất; đăng ký đúng sync hoặc `asyncTasks[]` trong `js.ts`.
- Không chuyển collector giữa sync/async khi chưa đo bằng `getPerformanceStats()`. Ưu tiên thay đổi nhỏ, đúng tầng.
