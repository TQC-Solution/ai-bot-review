# PubStar Android SDK — Kiến trúc & luật review

Tài liệu mô tả cấu trúc module, luật review và vùng thay đổi nhạy cảm của PubStar Android SDK (Kotlin/Java). Căn cứ: 📐 Coding Standards — Mobile SDK (PubStar) v1.0.
Nhãn mức độ: [chặn merge] = 🔴 · [cảnh báo] = ⚠️ · [nit] = 💡. Quy tắc không có nhãn là mô tả, không dùng để báo lỗi.
PR chạm Public API hoặc symbol CRITICAL (§4.1): luôn ghi rõ trong comment tổng kết, kể cả khi không có vi phạm, để người hiểu mediation review lại.

## 1. Tổng quan (multi-module Gradle)
- `:Pubstar`: core SDK (AAR) — domain logic, mediation orchestration, model, service, bridge nội bộ. Publish `io.pubstar.mobile:ads:<version>` (groupId có thể prefix `qa-`/`stage-`).
- `:PubStar*Adapter`: adapter mạng quảng cáo (AdMob, AppLovin, Facebook, Pangle...). Publish namespace riêng (`io.pubstar.mediation.adapter.*`...). Adapter → Core qua `implementation(project(":Pubstar"))` hoặc Maven.
- `:lib-ads`: thư viện phụ trợ (asset/layout/helper), tuân boundary như core internal.
- `:app`: sample/test app — không publish, không chứa logic SDK.
- Publish AAR lên Maven Central/Snapshots; version và groupId điều khiển bởi `ENV_TYPE`, `PUBLISH_TO_MAVEN_CENTRAL`, `VERSION`, `local.properties`.
- Phân tầng: Public API (ổn định signature) → Core Domain (orchestration, waterfall, cache, timeout, frequency, tracking) → Adapter (SDK bên thứ ba, callback về Core qua contract).

## 2. Luồng vận hành partner (xương sống mediation)
```
GetInitAdTask → AdapterController.initializeWithServerConfig
PubStarAd.loadAd / loadAndShowAd → GetAdModelTask → (PubStarAdConfigCache | PubStarFastPathLoadContext)
  → mergeAdNetIntoModelAndLoad → AdNet.loadAd → BaseAd / adapter partner
     → timeout (callCountDownTask / maxLoadTime) · frequency (checkIndexShow / SkipAdUnitProvider)
     → refresh (reloadAd / RefreshTimeProvider)
     → onError + rejectList → loadAndShowAd passback → GetAdModelTask
     → Native asRawData → PubStarNativeMediationBridge
```
- Init (`GetInitAdTask`): cache SP `TAG_INIT_CACHE`, giữ fallback khi mạng lỗi; `InitializeAdapterService` không load/show khi `!isSuccess`; `initializeWithServerConfig` chạy sau init thành công, không hardcode ORT URL/publisher.
- Waterfall (`GetAdModelTask`): timeout 20s; `createURLGetAd` + `skipConfigs` (`rejectList` ↔ passback, đồng bộ server); `onGetAdModelSuccess` giữ `configId`/`configTimeUpdateKey`/`order` và `activeAdLoadSessionByUnit`; `PubStarAdConfigCache` key `adUnitId | skipConfigs`; `PubStarFastPathLoadContext` không deliver sau `abortFastPath`/session hết hạn.
- `rejectList` = `configId` đã fail → passback; `callReject` = terminal `NO_AD` (clear reject). `mergeAdNetIntoModelAndLoad` không reorder `adNets`.
- Ngữ nghĩa `AdNet`: `timeDelay == -1` → tắt refresh · `timeOut`/`maxShow <= 0` → bỏ cap · `maxLoadTime` → load timeout · `configId` → identity waterfall · `isChangeRefresh` → `CHANGE_FREQUENCY`.
- Refresh: `reloadAd` + `TimeOutProvider` (theo `configId`); `reloadAd(View)` + `RefreshTimeProvider` + lifecycle; native raw: `deliverRawNativeDataIfRequested` → `reloadAd` + `registerRawMediationRefreshScheduler`.
- Timeout/frequency: `callCountDownTask` cancel trong `destroy`; `SkipAdUnitProvider` vs `SkipConfigProvider`; `callWhenError` với raw `asRawData` không thêm `configId` vào reject.
- Mediation bridge: `PubStarNativeMediationBridge` `@RestrictTo(LIBRARY_GROUP)`; `loadAdNetForMerge` giữ `adLoaderListener` khi `asRawData`; adapter publish chỉ map asset/tracker.
- Session (`PubStarAd`): `listKey` synchronized; `activeAdLoadSessionByUnit` bỏ response cũ; `scopeMain`/`scopeBackground`.

## 3. Luật review

### 3.1. Public API & visibility
- [chặn merge] Đổi/xoá package, class, signature public (class/listener/config app dùng trực tiếp) mà PR không ghi là breaking change có chủ đích.
- [cảnh báo] Type internal lộ trong signature public; `public` hoá class internal để gọi chéo (Kotlin mặc định `internal`, Java package-private).
- [cảnh báo] API mới sửa signature cũ thay vì overload/builder + deprecate; Public API chứa logic nghiệp vụ nặng.

### 3.2. Module boundary
- [chặn merge] Core phụ thuộc adapter publish (`project(":PubStar*Adapter")`, import `io.pubstar.mediation.adapter.*`); adapter A phụ thuộc adapter B.
- [chặn merge] Core import SDK quảng cáo bên thứ ba (trừ case đã duyệt); logic riêng một network đặt trong Core.
- [cảnh báo] Adapter tự hiện thực waterfall/passback/refresh thay vì để Core quyết định.
- [cảnh báo] Logic SDK đặt trong `:app`.

### 3.3. Không gọi controller từ nội bộ `:Pubstar`
- [chặn merge] Trong `Pubstar/src` (trừ `PubStarAd.kt` và ngoại lệ ở §5) gọi `getAdController().load|show|loadAndShow|isReady` hoặc `PubStarAdManager.getAdController()`.
- [chặn merge] Tạo `*Helper`/`*Bridge`/extension bọc controller; cast sang `PubStarAdControllerHelper`; adapter nhúng trong core gọi `loadAndShow` thay vì `AdNet` → `BaseAd`.
- [cảnh báo] Mediation native mới không mở rộng qua `NativeAdRequest`/SPI `PubStarNativeMediationBridge` mà thêm wrapper controller.

### 3.4. Vùng partner flow & CRITICAL (§4)
- [chặn merge] Đổi ngữ nghĩa magic value của `AdNet` (`timeDelay == -1`, `timeOut`/`maxShow <= 0`, `maxLoadTime`, `configId`, `isChangeRefresh`).
- [chặn merge] Gộp `loadAd` + `onGetAdModelSuccess` thành một hàm; reorder `adNets`; xoá `synchronized`/`sessionId`/`WeakReference` của refresh scheduler mà không có thay thế.
- [chặn merge] Lỗi mới không chọn rõ passback (`rejectList`) hay terminal (`callReject`/`NO_AD`).
- [cảnh báo] Đổi URL `GetAdModelTask` hoặc timeout 20s mà PR không ghi đã phối hợp backend/product.
- [cảnh báo] PR sửa symbol CRITICAL mà mô tả PR không có kế hoạch test §4.3 — dạng câu hỏi.
- [cảnh báo] PR sửa symbol HIGH (§4.2) mà không mô tả test hành vi — dạng câu hỏi.

### 3.5. Threading, lifecycle, memory
- [chặn merge] Giữ `Activity`/`View` quá lifecycle (field static, singleton, callback dài hạn); network/disk trên main thread.
- [chặn merge] `Handler`/coroutine/timer timeout mới không được cancel khi `destroy`.
- [cảnh báo] Callback UI không về main thread; state machine load/show có thể double-callback.

### 3.6. Lỗi, log, cấu hình, build
- [chặn merge] Log PII/credential/token/GAID; credential trong source.
- [cảnh báo] Public API throw khi không phải dùng sai rõ ràng; adapter không map lỗi network về error code Core.
- [cảnh báo] Log không theo `isShowLog`/`isDebug`.
- [cảnh báo] Hardcode URL production thay vì `BuildConfig`/`local.properties`.
- [cảnh báo] Commit `*/build/`, `BuildConfig.java`, `R.jar`, `R.txt`.
- [cảnh báo] Xoá keep rule đang cần; rule mới không đặt trong `consumer-rules.pro` (ưu tiên) hoặc `proguard-rules.pro` đúng module; đổi resource id đang dùng.
- [cảnh báo] Logic mediation trong class layout/view.
- [nit] Dependency bên thứ ba dùng `implementation` khi `compileOnly` phù hợp cho publish.

## 4. Change control
### 4.1. CRITICAL symbols
`PubStarAd.loadAd` / `loadAndShowAd` / `onGetAdModelSuccess` / `mergeAdNetIntoModelAndLoad` / `loadAdNetForMerge` / `callReject` · `GetAdModelTask` / `GetInitAdTask` · `BaseAdTimeOutAndMaxShow.reloadAd` / `deliverRawNativeDataIfRequested` / `callWhenError` · `PubStarNativeMediationBridge.loadNative` · `PubStarAdConfigCache` / `PubStarFastPathLoadContext` · `TimeOutProvider` / `RefreshTimeProvider` / `Skip*Provider` · `AdNet.loadAd` / `handleLoadAd`.
### 4.2. HIGH
`PubStarAdController.show`, `tryLoadSingleFromCachedAd`, field timing của `AdNet`, `AdapterController`, `InitializeAdapterService`, `Utils.convertToSkipConfigs`.
### 4.3. Test tối thiểu khi sửa CRITICAL
Init cold (có/không cache) · load 1 partner OK · fail A → passback B (`skipConfigs` trên URL) · refresh `timeDelay > 0` / `timeDelay = -1` không refresh · vượt cap → skip/`REJECT_BY_FREQUENCY` · AdMob/MAX native: load → display → refresh → terminal re-arm · `GetAdModelTask` mất mạng: fast path hoặc `NO_AD`.

## 5. Ngoại lệ / nợ kỹ thuật đã biết — KHÔNG báo trên code cũ
- `PubStarNativeMediationBridge.loadNative` gọi `getAdController().loadAndShow`: ngoại lệ duy nhất đã biết. Chỉ báo khi code MỚI nhân bản pattern này.
- `PubStarAd.kt` implement facade nên được gọi controller.

## 6. Nguyên tắc khi AI sửa/sinh code (không dùng để báo lỗi review)
- Package core `io.pubstar.mobile.*`; adapter namespace riêng; listener domain đặt ở Core.
- Refactor `loadNative` sang entry `loadAd` nội bộ khi có yêu cầu. Ưu tiên thay đổi nhỏ, giữ binary compatibility.
